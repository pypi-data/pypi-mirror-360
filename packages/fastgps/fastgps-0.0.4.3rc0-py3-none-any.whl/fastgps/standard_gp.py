from .abstract_gp import AbstractGP
from .util import (
    DummyDiscreteDistrib,
    _StandardInverseLogDetCache,
    tf_exp_eps,
    tf_exp_eps_inv,
    tf_identity,
)
import torch
import numpy as np
import qmcpy as qmcpy
from typing import Tuple,Union

class StandardGP(AbstractGP):
    """
    Standard Gaussian process regression
    
    Examples:
        >>> torch.set_default_dtype(torch.float64)

        >>> def f_ackley(x, a=20, b=0.2, c=2*np.pi, scaling=32.768):
        ...     # https://www.sfu.ca/~ssurjano/ackley.html
        ...     assert x.ndim==2
        ...     x = 2*scaling*x-scaling
        ...     t1 = a*torch.exp(-b*torch.sqrt(torch.mean(x**2,1)))
        ...     t2 = torch.exp(torch.mean(torch.cos(c*x),1))
        ...     t3 = a+np.exp(1)
        ...     y = -t1-t2+t3
        ...     return y

        >>> n = 2**6
        >>> d = 2
        >>> sgp = StandardGP(qmcpy.DigitalNetB2(dimension=d,seed=7))
        >>> x_next = sgp.get_x_next(n)
        >>> y_next = f_ackley(x_next)
        >>> sgp.add_y_next(y_next)

        >>> rng = torch.Generator().manual_seed(17)
        >>> x = torch.rand((2**7,d),generator=rng)
        >>> y = f_ackley(x)
        
        >>> pmean = sgp.post_mean(x)

        >>> pmean.shape
        torch.Size([128])
        >>> torch.linalg.norm(y-pmean)/torch.linalg.norm(y)
        tensor(0.0794)
        >>> torch.linalg.norm(sgp.post_mean(sgp.x)-sgp.y)/torch.linalg.norm(y)
        tensor(0.0524)

        >>> data = sgp.fit(verbose=0)
        >>> list(data.keys())
        ['iterations']

        >>> torch.linalg.norm(y-sgp.post_mean(x))/torch.linalg.norm(y)
        tensor(0.0832)
        >>> z = torch.rand((2**8,d),generator=rng)
        >>> pcov = sgp.post_cov(x,z)
        >>> pcov.shape
        torch.Size([128, 256])

        >>> pcov = sgp.post_cov(x,x)
        >>> pcov.shape
        torch.Size([128, 128])
        >>> assert (pcov.diagonal()>=0).all()

        >>> pvar = sgp.post_var(x)
        >>> pvar.shape
        torch.Size([128])
        >>> assert torch.allclose(pcov.diagonal(),pvar)

        >>> pmean,pstd,q,ci_low,ci_high = sgp.post_ci(x,confidence=0.99)
        >>> ci_low.shape
        torch.Size([128])
        >>> ci_high.shape
        torch.Size([128])

        >>> sgp.post_cubature_mean()
        tensor(20.0124)
        >>> sgp.post_cubature_var()
        tensor(0.0064)

        >>> pcmean,pcvar,q,pcci_low,pcci_high = sgp.post_cubature_ci(confidence=0.99)
        >>> pcci_low
        tensor(19.8063)
        >>> pcci_high
        tensor(20.2184)
        
        >>> pcov_future = sgp.post_cov(x,z,n=2*n)
        >>> pvar_future = sgp.post_var(x,n=2*n)
        >>> pcvar_future = sgp.post_cubature_var(n=2*n)
        
        >>> x_next = sgp.get_x_next(2*n)
        >>> y_next = f_ackley(x_next)
        >>> sgp.add_y_next(y_next)
        >>> torch.linalg.norm(y-sgp.post_mean(x))/torch.linalg.norm(y)
        tensor(0.1106)

        >>> assert torch.allclose(sgp.post_cov(x,z),pcov_future)
        >>> assert torch.allclose(sgp.post_var(x),pvar_future)
        >>> assert torch.allclose(sgp.post_cubature_var(),pcvar_future)

        >>> data = sgp.fit(verbose=False)
        >>> torch.linalg.norm(y-sgp.post_mean(x))/torch.linalg.norm(y)
        tensor(0.0627)

        >>> x_next = sgp.get_x_next(4*n)
        >>> y_next = f_ackley(x_next)
        >>> sgp.add_y_next(y_next)
        >>> torch.linalg.norm(y-sgp.post_mean(x))/torch.linalg.norm(y)
        tensor(0.1001)

        >>> data = sgp.fit(verbose=False)
        >>> torch.linalg.norm(y-sgp.post_mean(x))/torch.linalg.norm(y)
        tensor(0.0613)

        >>> pcov_16n = sgp.post_cov(x,z,n=16*n)
        >>> pvar_16n = sgp.post_var(x,n=16*n)
        >>> pcvar_16n = sgp.post_cubature_var(n=16*n)
        >>> x_next = sgp.get_x_next(16*n)
        >>> y_next = f_ackley(x_next)
        >>> sgp.add_y_next(y_next)
        >>> assert torch.allclose(sgp.post_cov(x,z),pcov_16n)
        >>> assert torch.allclose(sgp.post_var(x),pvar_16n)
        >>> assert torch.allclose(sgp.post_cubature_var(),pcvar_16n)
    """
    _XBDTYPE = torch.float64
    _FTOUTDTYPE = torch.float64
    def __init__(self,
            seqs:Union[qmcpy.IIDStdUniform,int],
            num_tasks:int = None,
            seed_for_seq:int = None,
            scale:float = 1., 
            lengthscales:Union[torch.Tensor,float] = 1., 
            noise:float = 1e-4,
            factor_task_kernel:Union[torch.Tensor,int] = 1.,
            rank_factor_task_kernel:int = None,
            noise_task_kernel:Union[torch.Tensor,float] = 1.,
            rq_param:float = 1.,
            device:torch.device = "cpu",
            tfs_scale:Tuple[callable,callable] = (tf_exp_eps_inv,tf_exp_eps),
            tfs_lengthscales:Tuple[callable,callable] = (tf_exp_eps_inv,tf_exp_eps),
            tfs_noise:Tuple[callable,callable] = (tf_exp_eps_inv,tf_exp_eps),
            tfs_factor_task_kernel:Tuple[callable,callable] = (tf_identity,tf_identity),
            tfs_noise_task_kernel:Tuple[callable,callable] = (tf_exp_eps_inv,tf_exp_eps),
            tfs_rq_param:Tuple[callable,callable] = (tf_exp_eps_inv,tf_exp_eps),
            requires_grad_scale:bool = True, 
            requires_grad_lengthscales:bool = True, 
            requires_grad_noise:bool = False, 
            requires_grad_factor_task_kernel:bool = None,
            requires_grad_noise_task_kernel:bool = None,
            requires_grad_rq_param:bool = True,
            shape_batch:torch.Size = torch.Size([]),
            shape_scale:torch.Size = torch.Size([1]), 
            shape_lengthscales:torch.Size = None,
            shape_noise:torch.Size = torch.Size([1]),
            shape_factor_task_kernel:torch.Size = None, 
            shape_noise_task_kernel:torch.Size = None,
            shape_rq_param:torch.Size = torch.Size([1]),
            derivatives:list = None,
            derivatives_coeffs:list = None,
            kernel_class:str = "Gaussian",
            adaptive_nugget:bool = True,
            data:dict = None,
            compile_dist_func:bool = False,
            compile_dist_func_kwargs:dict = {},
            gaussian_kernel_use_dist_func:bool = True,
            ):
        """
        Args:
            seqs (Union[int,qmcpy.DiscreteDistribution,List]]): list of sequence generators. If an int `d` is passed in we use 
                ```python
                [qmcpy.DigitalNetB2(d,seed=seed) for seed in np.random.SeedSequence(seed_for_seq).spawn(num_tasks)]
                ```
                See the <a href="https://qmcpy.readthedocs.io/en/latest/algorithms.html#discrete-distribution-class" target="_blank">`qmcpy.DiscreteDistribution` docs</a> for more info. 
            num_tasks (int): number of tasks 
            seed_for_seq (int): seed used for digital net randomization
            scale (float): kernel global scaling parameter
            lengthscales (Union[torch.Tensor[d],float]): vector of kernel lengthscales. 
                If a scalar is passed in then `lengthscales` is set to a constant vector. 
            noise (float): positive noise variance i.e. nugget term
            factor_task_kernel (Union[Tensor[num_tasks,rank_factor_task_kernel],int]): for $F$ the `factor_task_kernel` the task kernel is $FF^T + \\text{diag}(\\boldsymbol{v})$ 
                where `rank_factor_task_kernel<=num_tasks` and $\\boldsymbol{v}$ is the `noise_task_kernel`.
            rank_factor_task_kernel (int): see the description of `factor_task_kernel` above. Defaults to 0 for single task problems and 1 for multi task problems.
            noise_task_kernel (Union[torch.Tensor[num_tasks],float]): see the description of `factor_task_kernel` above 
            rq_param (float): scale mixture parameter for the rational quadratic kernel
            device (torch.device): torch device which is required to support `torch.float64`
            tfs_scale (Tuple[callable,callable]): the first argument transforms to the raw value to be optimized, the second applies the inverse transform
            tfs_lengthscales (Tuple[callable,callable]): the first argument transforms to the raw value to be optimized, the second applies the inverse transform
            tfs_noise (Tuple[callable,callable]): the first argument transforms to the raw value to be optimized, the second applies the inverse transform
            tfs_factor_task_kernel (Tuple[callable,callable]): the first argument transforms to the raw value to be optimized, the second applies the inverse transform
            tfs_noise_task_kernel (Tuple[callable,callable]): the first argument transforms to the raw value to be optimized, the second applies the inverse transform
            tfs_rq_param (Tuple[callable,callable]): the first argument transforms to the raw value to be optimized, the second applies the inverse transform
            requires_grad_scale (bool): wheather or not to optimize the scale parameter
            requires_grad_lengthscales (bool): wheather or not to optimize lengthscale parameters
            requires_grad_noise (bool): wheather or not to optimize the noise parameter
            requires_grad_factor_task_kernel (bool): wheather or not to optimize the factor for the task kernel
            requires_grad_noise_task_kernel (bool): wheather or not to optimize the noise for the task kernel
            requires_grad_rq_param (bool): wheather or not to optimize the mixture parameter for the rational quadratic kernel
            shape_batch (torch.Size): shape of the batch output for each task
            shape_scale (torch.Size): shape of the scale parameter, defaults to `torch.Size([1])`
            shape_lengthscales (torch.Size): shape of the lengthscales parameter, defaults to `torch.Size([d])` where `d` is the dimension
            shape_noise (torch.Size): shape of the noise parameter, defaults to `torch.Size([1])`
            shape_factor_task_kernel (torch.Size): shape of the factor for the task kernel, defaults to `torch.Size([num_tasks,r])` where `r` is the rank, see the description of `factor_task_kernel`
            shape_noise_task_kernel (torch.Size): shape of the noise for the task kernel, defaults to `torch.Size([num_tasks])`
            shape_rq_param (torch.Size): shape of the mixture parameter for the rational quadratic kernel `torch.Size([1])`
            derivatives (list): list of derivative orders e.g. to include a function and its gradient set 
                ```python
                derivatives = [torch.zeros(d,dtype=int)]+[ej for ej in torch.eye(d,dtype=int)]
                ```
            derivatives_coeffs (list): list of derivative coefficients where if `derivatives[k].shape==(p,d)` then we should have `derivatives_coeffs[k].shape==(p,)`
            adaptive_nugget (bool): if True, use the adaptive nugget which modifies noises based on trace ratios.  
            data (dict): dictory of data with keys 'x' and 'y' where data['x'] and data['y'] are both `torch.Tensor`s or list of `torch.Tensor`s with lengths equal to the number of tasks
            compile_dist_func (bool): if `True`, use compile the pairwise distance function for memory efficiency when evaluating the kernel matrix.
            compile_dist_func_kwargs (dict): keyword arguments to `torch.compile` used when `compile_dist_func=True`.
            gaussian_kernel_use_dist_func (bool): if `True`, use the distance function to compute the Gaussian kernel, otherwise use the product of exponentials
        """
        if num_tasks is None: 
            solo_task = True
            default_task = 0 
            num_tasks = 1
        else:
            assert isinstance(num_tasks,int) and num_tasks>0
            solo_task = False
            default_task = torch.arange(num_tasks)
        if data is not None:
            assert isinstance(seqs,int), "passing in data requires seqs (the first argument) is a int specifying the dimension"
            assert isinstance(data,dict) and "x" in data and "y" in data, "data must be a dict with keys 'x' and 'y'"
            if isinstance(data["x"],torch.Tensor): data["x"] = [data["x"]]
            if isinstance(data["y"],torch.Tensor): data["y"] = [data["y"]]
            assert isinstance(data["x"],list) and len(data["x"])==num_tasks and all(isinstance(x_l,torch.Tensor) and x_l.ndim==2 and x_l.size(1)==seqs for x_l in data["x"]), "data['x'] should be a list of 2d tensors of length num_tasks with each number of columns equal to the dimension"
            assert isinstance(data["y"],list) and len(data["y"])==num_tasks and all(isinstance(y_l,torch.Tensor) and y_l.ndim>=1 for y_l in data["y"]), "data['y'] should be a list of tensors of length num_tasks"
            seqs = np.array([DummyDiscreteDistrib(data["x"][l].cpu().detach().numpy()) for l in range(num_tasks)],dtype=object)
        else:
            if isinstance(seqs,int):
                seqs = np.array([qmcpy.DigitalNetB2(seqs,seed=seed,order="GRAY") for seed in np.random.SeedSequence(seed_for_seq).spawn(num_tasks)],dtype=object)
            if isinstance(seqs,qmcpy.DiscreteDistribution):
                seqs = np.array([seqs],dtype=object)
            if isinstance(seqs,list):
                seqs = np.array(seqs,dtype=object)
        assert seqs.shape==(num_tasks,), "seqs should be a length num_tasks=%d list"%num_tasks
        assert all(seqs[i].replications==1 for i in range(num_tasks)) and "each seq should have only 1 replication"
        kernel_class = kernel_class.lower()
        self.available_kernel_classes = ['gaussian','matern12','matern32','matern52','rq']
        assert kernel_class in self.available_kernel_classes, "kernel_class must in %s"%str(self.available_kernel_classes)
        self.kernel_class = kernel_class
        assert isinstance(compile_dist_func,bool)
        assert isinstance(gaussian_kernel_use_dist_func,bool)
        self.gaussian_kernel_use_dist_func = gaussian_kernel_use_dist_func
        if self.kernel_class=="gaussian" and (not self.gaussian_kernel_use_dist_func):
            self.gaussian_kernel = lambda x1,x2,lengthscales: torch.exp(-((x1-x2)/(np.sqrt(2)*lengthscales))**2).prod(-1)
            if compile_dist_func:
                self.gaussian_kernel = torch.compile(self.gaussian_kernel,**compile_dist_func_kwargs)
        else:
            self.pairwise_rel_dist_func = lambda x1,x2,lengthscales: torch.linalg.norm((x1-x2)/(np.sqrt(2)*lengthscales),ord=2,dim=-1)
            if compile_dist_func:
                self.pairwise_rel_dist_func = torch.compile(self.pairwise_rel_dist_func,**compile_dist_func_kwargs)
        super().__init__(
            seqs,
            num_tasks,
            default_task,
            solo_task,
            scale,
            lengthscales,
            noise,
            factor_task_kernel,
            rank_factor_task_kernel,
            noise_task_kernel,
            device,
            tfs_scale,
            tfs_lengthscales,
            tfs_noise,
            tfs_factor_task_kernel,
            tfs_noise_task_kernel,
            requires_grad_scale,
            requires_grad_lengthscales,
            requires_grad_noise,
            requires_grad_factor_task_kernel,
            requires_grad_noise_task_kernel,
            shape_batch,
            shape_scale, 
            shape_lengthscales,
            shape_noise,
            shape_factor_task_kernel, 
            shape_noise_task_kernel,
            derivatives,
            derivatives_coeffs,
            adaptive_nugget,
        )
        if data is not None:
            self.add_y_next(data["y"],task=torch.arange(self.num_tasks))
        if self.kernel_class=="rq":
            # rq param
            assert np.isscalar(rq_param) or isinstance(rq_param,torch.Tensor), "rq_param must be a scalar or torch.Tensor"
            if isinstance(rq_param,torch.Tensor): shape_rq_param = rq_param.shape
            if isinstance(shape_rq_param,(list,tuple)): shape_rq_param = torch.Size(shape_rq_param)
            assert isinstance(shape_rq_param,torch.Size) and shape_rq_param[-1]==1
            if len(shape_rq_param)>1: assert shape_rq_param[:-1]==shape_batch[-(len(shape_rq_param)-1):]
            if np.isscalar(rq_param): rq_param = rq_param*torch.ones(shape_rq_param,device=self.device)
            assert (rq_param>0).all(), "rq_param must be positive"
            assert len(tfs_rq_param)==2 and callable(tfs_rq_param[0]) and callable(tfs_rq_param[1]), "tfs_rq_param should be a tuple of two callables, the transform and inverse transform"
            self.tf_rq_param = tfs_rq_param[1]
            self.raw_rq_param = torch.nn.Parameter(tfs_rq_param[0](rq_param),requires_grad=requires_grad_rq_param)
        if self.kernel_class=="gaussian" and self.gaussian_kernel_use_dist_func:
            assert all((deriv==0).all() for deriv in self.derivatives), "set gaussian_kernel_use_dist_func=False when using derivatives"
    @property
    def rq_param(self):
        """
        Kernel lengthscale parameter.
        """
        assert self.kernel_class=="rq", "rq_param only available for the rational quadratic (RQ) kernel class"
        return self.tf_rq_param(self.raw_rq_param)
    def get_inv_log_det_cache(self, n=None):
        if n is None: n = self.n
        assert isinstance(n,torch.Tensor) and n.shape==(self.num_tasks,) and (n>=self.n).all()
        ntup = tuple(n.tolist())
        if ntup not in self.inv_log_det_cache_dict.keys():
            self.inv_log_det_cache_dict[ntup] = _StandardInverseLogDetCache(self,n)
        return self.inv_log_det_cache_dict[ntup]
    def _kernel(self, x:torch.Tensor, z:torch.Tensor, beta0:torch.Tensor, beta1: torch.Tensor, c0:torch.Tensor, c1:torch.Tensor):
        assert c0.ndim==1 and c1.ndim==1
        assert beta0.shape==(len(c0),self.d) and beta1.shape==(len(c1),self.d)
        assert x.size(-1)==self.d and z.size(-1)==self.d
        incoming_grad_enabled = torch.is_grad_enabled()
        torch.set_grad_enabled(True)
        if (beta0>0).any():
            xtileshape = tuple(torch.ceil(torch.tensor(z.shape[:-1])/torch.tensor(x.shape[:-1])).to(int))
            xgs = [torch.tile(x[...,j].clone().requires_grad_(True),xtileshape) for j in range(self.d)]
            [xgj.requires_grad_(True) for xgj in xgs]
            xg = torch.stack(xgs,dim=-1)
        else:
            xg = x
        if (beta1>0).any():
            ztileshape = tuple(torch.ceil(torch.tensor(x.shape[:-1])/torch.tensor(z.shape[:-1])).to(int))
            zgs = [torch.tile(z[...,j].clone().requires_grad_(True),ztileshape) for j in range(self.d)]
            [zgj.requires_grad_(True) for zgj in zgs]
            zg = torch.stack(zgs,dim=-1)
        else:
            zg = z
        y = 0
        ndim = xg.ndim
        lengthscales = self.lengthscales.reshape(list(self.lengthscales.shape)[:-1]+[1]*(ndim-1)+[self.lengthscales.size(-1)])
        scale = self.scale.reshape(list(self.scale.shape)[:-1]+[1]*(ndim-1))
        if self.kernel_class=="gaussian":
            if self.gaussian_kernel_use_dist_func:
                dists = self.pairwise_rel_dist_func(xg,zg,lengthscales)
                y_base = scale*torch.exp(-dists**2)
            else:
                y_base = scale*self.gaussian_kernel(xg,zg,lengthscales)
        elif self.kernel_class=="matern12":
            dists = self.pairwise_rel_dist_func(xg,zg,lengthscales)
            y_base = scale*torch.exp(-dists)
        elif self.kernel_class=="matern32":
            dists = self.pairwise_rel_dist_func(xg,zg,lengthscales)
            y_base = scale*(1+np.sqrt(3)*dists)*torch.exp(-np.sqrt(3)*dists)
        elif self.kernel_class=="matern52":
            dists = self.pairwise_rel_dist_func(xg,zg,lengthscales)
            y_base = scale*((1+np.sqrt(5)*dists+5*dists**2/3)*torch.exp(-np.sqrt(5)*dists))
        elif self.kernel_class=="rq":
            dists = self.pairwise_rel_dist_func(xg,zg,lengthscales)
            rq_param = self.rq_param.reshape(list(self.rq_param.shape)[:-1]+[1]*(ndim-1))
            y_base = scale*(1+dists**2/rq_param)**(-rq_param)
        else:
            raise Exception("kernel_class must be in %s"%str(self.available_kernel_classes))
        for i0 in range(len(c0)):
            for i1 in range(len(c1)):
                if (beta0[i0]>0).any() or (beta1[i1]>0).any():
                    y_part = y_base.clone()
                    for j0 in range(self.d):
                        for k in range(beta0[i0,j0]):
                            y_part = torch.autograd.grad(y_part,xgs[j0],grad_outputs=torch.ones_like(y_part,requires_grad=True),create_graph=True)[0]
                    for j1 in range(self.d):
                        for k in range(beta1[i1,j1]):
                            y_part = torch.autograd.grad(y_part,zgs[j1],grad_outputs=torch.ones_like(y_part,requires_grad=True),create_graph=True)[0]
                else:
                    y_part = y_base 
                y += c0[i0]*c1[i1]*y_part
        torch.set_grad_enabled(incoming_grad_enabled)
        return y
    def post_cubature_mean(self, task:Union[int,torch.Tensor]=None, eval:bool=True, integrate_unit_cube:bool=True):
        kmat_tasks = self.gram_matrix_tasks
        coeffs = self.coeffs
        if eval:
            incoming_grad_enabled = torch.is_grad_enabled()
            torch.set_grad_enabled(False)
        if task is None: task = self.default_task
        inttask = isinstance(task,int)
        if inttask: task = torch.tensor([task],dtype=int)
        if isinstance(task,list): task = torch.tensor(task,dtype=int)
        assert task.ndim==1 and (task>=0).all() and (task<self.num_tasks).all()
        assert self.kernel_class=="gaussian", "so far, we have only worked out integrals for the Gaussian kernel"
        norms = [torch.distributions.Normal(self.get_x(l),self.lengthscales[...,None,:]) for l in range(self.num_tasks)]
        lb,ub = (torch.tensor([0],device=self.device),torch.tensor([1],device=self.device)) if integrate_unit_cube else (torch.tensor([-torch.inf],device=self.device),torch.tensor([torch.inf],device=self.device))
        kint_parts = [self.scale*(np.sqrt(2*np.pi)*self.lengthscales[...,None,:]*(norms[l].cdf(ub)-norms[l].cdf(lb))).prod(-1) for l in range(self.num_tasks)]
        kints = torch.cat([kmat_tasks[...,task,l,None]*kint_parts[l][...,None,:] for l in range(self.num_tasks)],dim=-1)
        pcmean = (kints*coeffs[...,None,:]).sum(-1)
        if eval:
            torch.set_grad_enabled(incoming_grad_enabled)
        return pcmean[...,0] if inttask else pcmean
    def post_cubature_var(self, task:Union[int,torch.Tensor]=None, n:Union[int,torch.Tensor]=None, eval:bool=True, integrate_unit_cube:bool=True):
        assert integrate_unit_cube, "undefinted posterior variance when integrating first term over all reals"
        if n is None: n = self.n
        if isinstance(n,int): n = torch.tensor([n],dtype=int,device=self.device)
        assert isinstance(n,torch.Tensor)
        kmat_tasks = self.gram_matrix_tasks
        inv_log_det_cache = self.get_inv_log_det_cache(n)
        thetainv = inv_log_det_cache()[0]
        if eval:
            incoming_grad_enabled = torch.is_grad_enabled()
            torch.set_grad_enabled(False)
        if task is None: task = self.default_task
        inttask = isinstance(task,int)
        if inttask: task = torch.tensor([task],dtype=int)
        if isinstance(task,list): task = torch.tensor(task,dtype=int)
        assert task.ndim==1 and (task>=0).all() and (task<self.num_tasks).all()
        assert self.kernel_class=="gaussian", "so far, we have only worked out integrals for the Gaussian kernel"
        norms = [torch.distributions.Normal(self.get_x(l,n=n[l]),self.lengthscales[...,None,:]) for l in range(self.num_tasks)]
        lb,ub = (torch.tensor([0],device=self.device),torch.tensor([1],device=self.device)) if integrate_unit_cube else (torch.tensor([-torch.inf],device=self.device),torch.tensor([torch.inf],device=self.device))
        kint_parts = [self.scale*(np.sqrt(2*np.pi)*self.lengthscales[...,None,:]*(norms[l].cdf(ub)-norms[l].cdf(lb))).prod(-1) for l in range(self.num_tasks)]
        kints = torch.cat([kmat_tasks[...,task,l,None]*kint_parts[l][...,None,:] for l in range(self.num_tasks)],dim=-1)
        v = torch.einsum("...ij,...j->...i",thetainv[...,None,:,:],kints)
        l_d = self.lengthscales+torch.zeros(self.d,device=self.device)
        t = 2*(-1+torch.exp(-1/(2*l_d**2)))*l_d**2+np.sqrt(2*np.pi)*l_d*torch.erf(1/(np.sqrt(2)*l_d))
        tval = self.scale*kmat_tasks[...,task,task]*t.prod(-1)[...,None]
        pcvar = tval-(kints*v).sum(-1)
        pcvar[pcvar<0] = 0.
        if eval:
            torch.set_grad_enabled(incoming_grad_enabled)
        return pcvar[...,0] if inttask else pcvar
    def post_cubature_cov(self, task0:Union[int,torch.Tensor]=None, task1:Union[int,torch.Tensor]=None, n:Union[int,torch.Tensor]=None, eval:bool=True, integrate_unit_cube:bool=True):
        assert integrate_unit_cube, "undefinted posterior variance when integrating first term over all reals"
        if n is None: n = self.n
        if isinstance(n,int): n = torch.tensor([n],dtype=int,device=self.device)
        assert isinstance(n,torch.Tensor)
        kmat_tasks = self.gram_matrix_tasks
        inv_log_det_cache = self.get_inv_log_det_cache(n)
        thetainv = inv_log_det_cache()[0]
        if eval:
            incoming_grad_enabled = torch.is_grad_enabled()
            torch.set_grad_enabled(False)
        if task0 is None: task0 = self.default_task
        inttask0 = isinstance(task0,int)
        if inttask0: task0 = torch.tensor([task0],dtype=int)
        if isinstance(task0,list): task0 = torch.tensor(task0,dtype=int)
        assert task0.ndim==1 and (task0>=0).all() and (task0<self.num_tasks).all()
        if task1 is None: task1 = self.default_task
        inttask1 = isinstance(task1,int)
        if inttask1: task1 = torch.tensor([task1],dtype=int)
        if isinstance(task1,list): task1 = torch.tensor(task1,dtype=int)
        assert task1.ndim==1 and (task1>=0).all() and (task1<self.num_tasks).all()
        assert self.kernel_class=="gaussian", "so far, we have only worked out integrals for the Gaussian kernel"
        equal = torch.equal(task0,task1)
        norms = [torch.distributions.Normal(self.get_x(l,n=n[l]),self.lengthscales[...,None,:]) for l in range(self.num_tasks)]
        lb,ub = (torch.tensor([0],device=self.device),torch.tensor([1],device=self.device)) if integrate_unit_cube else (torch.tensor([-torch.inf],device=self.device),torch.tensor([torch.inf],device=self.device))
        kint_parts = [self.scale*(np.sqrt(2*np.pi)*self.lengthscales[...,None,:]*(norms[l].cdf(ub)-norms[l].cdf(lb))).prod(-1) for l in range(self.num_tasks)]
        kints0 = torch.cat([kmat_tasks[...,task0,l,None]*kint_parts[l][...,None,:] for l in range(self.num_tasks)],dim=-1)
        kints1 = torch.cat([kmat_tasks[...,task1,l,None]*kint_parts[l][...,None,:] for l in range(self.num_tasks)],dim=-1)
        v = torch.einsum("...ij,...j->...i",thetainv[...,None,:,:],kints1)
        l_d = self.lengthscales+torch.zeros(self.d,device=self.device)
        t = 2*(-1+torch.exp(-1/(2*l_d**2)))*l_d**2+np.sqrt(2*np.pi)*l_d*torch.erf(1/(np.sqrt(2)*l_d))
        tval = self.scale[...,None]*kmat_tasks[...,task0,:][...,:,task1]*t.prod(-1)[...,None,None]
        pccov = tval-(kints0[...,:,None,:]*v[...,None,:,:]).sum(-1)
        if equal:
            tvec = torch.arange(pccov.size(-1))
            diag = pccov[...,tvec,tvec]
            diag[diag<0] = 0. 
            pccov[...,tvec,tvec] = diag
        if eval:
            torch.set_grad_enabled(incoming_grad_enabled)
        if inttask0 and inttask1:
            return pccov[...,0,0]
        elif inttask0 and not inttask1:
            return pccov[...,0,:]
        elif not inttask0 and inttask1:
            return pccov[...,:,0]
        else: #not inttask0 and not inttask1
            return pccov
    
