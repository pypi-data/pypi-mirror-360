
from . import mapz
from buildz import xf
from ..base import Base
import os
def dzkeys(key, spt):
    if key is None:
        return []
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
            self.stacks = {}
            self._links = [{},None]
        self.dr_bind('_get', 'get')
        self.dr_bind('_hget', 'hget')
        self.dr_bind('_set', 'set')
        self.dr_bind('_has', 'has')
        self.dr_bind('_remove', 'remove')
        self.dr_bind('_link', 'link')
        self.dr_bind('_unlink', 'unlink')
        self.dr_bind('_push', 'push')
        self.dr_bind('_pop', 'pop')
        self.dr_bind('_stack_set', 'stack_set')
        self.dr_bind('_stack_unset', 'stack_unset')
        self.fcs_bind('get', 'gets', False, True)
        self.fcs_bind('set', 'sets', True)
        self.fcs_bind('remove', 'removes')
        self.fcs_bind('push', 'pushs', True)
        self.fcs_bind('pop', 'pops')
        self.fcs_bind('stack_set', 'stack_sets', True)
        self.fcs_bind('stack_unset', 'stack_unsets')
        self.fcs_bind('link', 'links', True)
        self.fcs_bind('unlink', 'unlinks')
        for name,rename in zip("stack_set,stack_unset,stack_sets,stack_unsets".split(","), "tmp_set,tmp_unset,tmp_sets,tmp_unsets".split(',')):
            setattr(self, rename, getattr(self, name))
        self.have_all = self.has_all
    def clean(self):
        obj = self.root or self
        obj.conf = {}
        obj.stacks = {}
        obj._links = [{}, None]
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
    def fcs_bind(self, fn, wfn, align=False, null_default= False):
        def wfc(keys, *objs, **maps):
            keys = self.spts_ks(keys)
            fc = getattr(self, fn)
            rst = []
            for i in range(len(keys)):
                if i<len(objs):
                    val = fc(keys[i], objs[i], **maps)
                else:
                    if align:
                        raise Exception(f"not val[{i}]")
                    if null_default:
                        val = fc(keys[i], None, **maps)
                    else:
                        val = fc(keys[i], **maps)
                rst.append(val)
            return rst
        setattr(self, wfn, wfc)
    def _stack_set(self, key, val):
        if key not in self.stacks:
            self.stacks[key] = []
        self.stacks[key] = [val]
    def _stack_unset(self, key, val):
        if key not in self.stacks:
            return False
        del self.stacks[key]
        return True
    def _push(self, key, val):
        if key not in self.stacks:
            self.stacks[key] = []
        self.stacks[key].append(val)
    def _pop(self, key):
        if key not in self.stacks:
            return False
        stk = self.stacks[key]
        if len(stk)==0:
            return False
        stk.pop(-1)
        return True
    def _link(self, src, target):
        keys = dzkeys(src, self.spt)
        links = self._links
        for key in keys:
            if key not in links[0]:
                links[0][key] = [{},None]
            links = links[0][key]
        links[1] = target
    def _unlink(self, key):
        keys = dzkeys(key, self.spt)
        links = self._links
        for key in keys:
            if key not in links[0]:
                return False
            links = links[0][key]
        links[1] = None
        return True
    def link_match(self, keys):
        obj = self.root or self
        links = obj._links
        deep = 0
        for key in keys:
            if key not in links[0]:
                break
            deep+=1
            links = links[0][key]
        return links[1], deep
    def _set(self, key, val):
        keys = dzkeys(key, self.spt)
        mapz.dset(self.conf, keys, val)
    def _hget(self, key, default=None, loop=-1):
        #print(f"_hget: {key}, {default}, {loop}")
        stk = mapz.get(self.stacks, key, [])
        if len(stk)>0:
            return stk[-1],1
        keys = dzkeys(key, self.spt)
        val, find = mapz.dget(self.conf, keys, default)
        if find or loop==0:
            return val, find
        lnk, deep = self.link_match(keys)
        if lnk is None:
            return val, find
        keys = keys[deep:]
        keys = self.spt.join(keys)
        key = lnk+self.spt+keys
        if loop>0:
            loop-=1
        return self._hget(key, default, loop)
    def _get(self, key, default=None, loop=-1):
        return self._hget(key, default,loop)[0]
        keys = dzkeys(key, self.spt)
        return mapz.dget(self.conf, keys, default)[0]
    def _remove(self, key):
        keys = dzkeys(key, self.spt)
        return mapz.dremove(self.conf, keys)
    def _has(self, key, loop=0):
        return self._hget(key, None, loop)[1]
        keys = dzkeys(key, self.spt)
        return mapz.dhas(self.conf, keys)
    def spts_ks(self, keys):
        keys = dzkeys(keys, self.spts)
        keys = [k.strip() if type(k) == str else k for k in keys]
        return keys
    # def gets(self, keys, *defaults):
    #     keys = self.spts_ks(keys)
    #     rst = []
    #     for i in range(len(keys)):
    #         val = self.get(keys[i], defaults[i] if i<len(defaults) else None)
    #         rst.append(val)
    #     return rst
    # def pushs(self, keys, *vals):
    #     keys = self.spts_ks(keys)
    #     rst = [self.push(key, val) for key, val in zip(keys, vals)]
    # def pops(self, keys):
    #     keys = self.spts_ks(keys)
    #     return [self.pop(key) for key in keys]
    def g(self, **maps):
        return [self.get(k, v) for k,v in maps.items()]
    def s(self, **maps):
        [self.set(k,v) for k,v in maps.items()]
    # def sets(self, keys, *vals):
    #     keys = self.spts_ks(keys)
    #     rst = [self.set(key, val) for key, val in zip(keys, vals)]
    # def removes(self, keys):
    #     keys = self.spts_ks(keys)
    #     rst = [self.remove(key) for key in keys]
    def has_all(self, keys, loop = 0):
        keys = self.spts_ks(keys)
        rst = [1-self.has(key, loop) for key in keys]
        return sum(rst)==0
    def has_any(self, keys, loop=0):
        keys = self.spts_ks(keys)
        for key in keys:
            if self.has(key, loop):
                return True
        return False