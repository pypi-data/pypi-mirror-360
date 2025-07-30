
from . import mapz
from buildz import xf
from ..base import Base
import os
def dzkeys(key, spt):
    # return mapz.keys(key, spt)
    if type(key)==str:
        key = key.split(spt)
    if type(key) not in (list, tuple):
        key = [key]
    return key
class Conf(Base):
    def val(self):
        return self.get_conf()
    def top(self, domain = None):
        root = self.root or self
        if domain is not None:
            root = root(domain)
        return root
        # return self.root or self
    def get_conf(self):
        if self.domain:
            key = self.domain
        obj = self.root or self
        if self.domain:
            return obj._get(self.domain)
        return obj.conf
    def str(self):
        return str(self.get_conf())
    def call(self, domain=None):
        if domain is None:
            return self.top()
        if self.domain:
            domain = self.domain+self.spt+domain
        obj = self.root or self
        return Conf(self.spt, self.spts, domain, obj)
    def init(self, spt='.', spts=',', domain=None, root = None):
        self.spt = spt
        self.spts = spts
        self.domain = domain
        self.root = root
        if root is None:
            self.conf = {}
        self.dr_bind('_get', 'get')
        self.dr_bind('_hget', 'hget')
        self.dr_bind('_set', 'set')
        self.dr_bind('_has', 'has')
        self.dr_bind('_remove', 'remove')
        self.have_all = self.has_all
    def clean(self):
        obj = self.root or self
        obj.conf = {}
        return self
    def dkey(self, key):
        if self.domain:
            key = self.domain+self.spt+key
        return key
    def update(self, conf, flush = 1, replace=1, visit_list=0):
        if self.domain:
            ks = dzkeys(self.domain, self.spt)
            tmp = {}
            mapz.dset(tmp, ks, conf)
            conf = tmp
        if self.root:
            return self.root.update(conf, flush, replace, visit_list)
        if flush:
            conf = xf.flush_maps(conf, lambda x:x.split(self.spt) if type(x)==str else [x], visit_list)
        xf.fill(conf, self.conf, replace=replace)
        return self
    def dr_bind(self, fn, wfn):
        def wfc(key,*a,**b):
            key = self.dkey(key)
            obj = self.root or self
            fc = getattr(obj, fn)
            return fc(key, *a, **b)
        setattr(self, wfn, wfc)
    def _set(self, key, val):
        keys = dzkeys(key, self.spt)
        mapz.dset(self.conf, keys, val)
    def _hget(self, key, default=None):
        keys = dzkeys(key, self.spt)
        return mapz.dget(self.conf, keys, default)
    def _get(self, key, default=None):
        return self._hget(key, default)[0]
        keys = dzkeys(key, self.spt)
        return mapz.dget(self.conf, keys, default)[0]
    def _remove(self, key):
        keys = dzkeys(key, self.spt)
        return mapz.dremove(self.conf, keys)
    def _has(self, key):
        keys = dzkeys(key, self.spt)
        return mapz.dhas(self.conf, keys)
    def spts_ks(self, keys):
        keys = dzkeys(keys, self.spts)
        keys = [k.strip() if type(k) == str else k for k in keys]
        return keys
    def gets(self, keys, *defaults):
        keys = self.spts_ks(keys)
        rst = []
        for i in range(len(keys)):
            val = self.get(keys[i], defaults[i] if i<len(defaults) else None)
            rst.append(val)
        return rst
    def g(self, **maps):
        return [self.get(k, v) for k,v in maps.items()]
    def s(self, **maps):
        [self.set(k,v) for k,v in maps.items()]
    def sets(self, keys, *vals):
        keys = self.spts_ks(keys)
        rst = [self.set(key, val) for key, val in zip(keys, vals)]
    def removes(self, keys):
        keys = self.spts_ks(keys)
        rst = [self.remove(key) for key in keys]
    def has_all(self, keys):
        keys = self.spts_ks(keys)
        rst = [1-self.has(key) for key in keys]
        return sum(rst)==0
    def has_any(self, keys):
        keys = self.spts_ks(keys)
        for key in keys:
            if self.has(key):
                return True
        return False