var Un = Object.defineProperty;
var Gn = (e, t, n) => t in e ? Un(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var $ = (e, t, n) => Gn(e, typeof t != "symbol" ? t + "" : t, n);
import * as Hn from "vue";
import { unref as M, watch as K, nextTick as ke, isRef as Kt, ref as J, shallowRef as G, watchEffect as zt, computed as W, toRaw as qt, customRef as ie, toValue as Je, readonly as Kn, provide as ae, inject as z, shallowReactive as zn, defineComponent as D, reactive as qn, h as x, getCurrentInstance as Qt, renderList as Qn, TransitionGroup as Jt, cloneVNode as Ne, withDirectives as Yt, normalizeStyle as Jn, normalizeClass as Ve, toDisplayString as $e, vModelDynamic as Yn, vShow as Xn, resolveDynamicComponent as Zn, normalizeProps as er, onErrorCaptured as tr, openBlock as se, createElementBlock as ve, createElementVNode as nr, createVNode as rr, createCommentVNode as or, createBlock as sr, Teleport as ir, renderSlot as ar, Fragment as cr, KeepAlive as ur } from "vue";
let Xt;
function lr(e) {
  Xt = e;
}
function Ye() {
  return Xt;
}
function Ce() {
  const { queryPath: e, pathParams: t, queryParams: n } = Ye();
  return {
    path: e,
    ...t === void 0 ? {} : { params: t },
    ...n === void 0 ? {} : { queryParams: n }
  };
}
const dt = /* @__PURE__ */ new Map();
function fr(e) {
  var t;
  (t = e.scopes) == null || t.forEach((n) => {
    dt.set(n.id, n);
  });
}
function Ge(e) {
  return dt.get(e);
}
function Re(e) {
  return e && dt.has(e);
}
function pe(e) {
  return typeof e == "function" ? e() : M(e);
}
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const Xe = () => {
};
function Ze(e, t = !1, n = "Timeout") {
  return new Promise((r, o) => {
    setTimeout(t ? () => o(n) : r, e);
  });
}
function et(e, t = !1) {
  function n(c, { flush: f = "sync", deep: h = !1, timeout: g, throwOnTimeout: m } = {}) {
    let v = null;
    const b = [new Promise((R) => {
      v = K(
        e,
        (N) => {
          c(N) !== t && (v ? v() : ke(() => v == null ? void 0 : v()), R(N));
        },
        {
          flush: f,
          deep: h,
          immediate: !0
        }
      );
    })];
    return g != null && b.push(
      Ze(g, m).then(() => pe(e)).finally(() => v == null ? void 0 : v())
    ), Promise.race(b);
  }
  function r(c, f) {
    if (!Kt(c))
      return n((N) => N === c, f);
    const { flush: h = "sync", deep: g = !1, timeout: m, throwOnTimeout: v } = f ?? {};
    let _ = null;
    const R = [new Promise((N) => {
      _ = K(
        [e, c],
        ([j, U]) => {
          t !== (j === U) && (_ ? _() : ke(() => _ == null ? void 0 : _()), N(j));
        },
        {
          flush: h,
          deep: g,
          immediate: !0
        }
      );
    })];
    return m != null && R.push(
      Ze(m, v).then(() => pe(e)).finally(() => (_ == null || _(), pe(e)))
    ), Promise.race(R);
  }
  function o(c) {
    return n((f) => !!f, c);
  }
  function s(c) {
    return r(null, c);
  }
  function i(c) {
    return r(void 0, c);
  }
  function u(c) {
    return n(Number.isNaN, c);
  }
  function l(c, f) {
    return n((h) => {
      const g = Array.from(h);
      return g.includes(c) || g.includes(pe(c));
    }, f);
  }
  function d(c) {
    return a(1, c);
  }
  function a(c = 1, f) {
    let h = -1;
    return n(() => (h += 1, h >= c), f);
  }
  return Array.isArray(pe(e)) ? {
    toMatch: n,
    toContains: l,
    changed: d,
    changedTimes: a,
    get not() {
      return et(e, !t);
    }
  } : {
    toMatch: n,
    toBe: r,
    toBeTruthy: o,
    toBeNull: s,
    toBeNaN: u,
    toBeUndefined: i,
    changed: d,
    changedTimes: a,
    get not() {
      return et(e, !t);
    }
  };
}
function dr(e) {
  return et(e);
}
function hr(e, t, n) {
  let r;
  Kt(n) ? r = {
    evaluating: n
  } : r = n || {};
  const {
    lazy: o = !1,
    evaluating: s = void 0,
    shallow: i = !0,
    onError: u = Xe
  } = r, l = J(!o), d = i ? G(t) : J(t);
  let a = 0;
  return zt(async (c) => {
    if (!l.value)
      return;
    a++;
    const f = a;
    let h = !1;
    s && Promise.resolve().then(() => {
      s.value = !0;
    });
    try {
      const g = await e((m) => {
        c(() => {
          s && (s.value = !1), h || m();
        });
      });
      f === a && (d.value = g);
    } catch (g) {
      u(g);
    } finally {
      s && f === a && (s.value = !1), h = !0;
    }
  }), o ? W(() => (l.value = !0, d.value)) : d;
}
function pr(e, t, n) {
  const {
    immediate: r = !0,
    delay: o = 0,
    onError: s = Xe,
    onSuccess: i = Xe,
    resetOnExecute: u = !0,
    shallow: l = !0,
    throwError: d
  } = {}, a = l ? G(t) : J(t), c = J(!1), f = J(!1), h = G(void 0);
  async function g(_ = 0, ...b) {
    u && (a.value = t), h.value = void 0, c.value = !1, f.value = !0, _ > 0 && await Ze(_);
    const R = typeof e == "function" ? e(...b) : e;
    try {
      const N = await R;
      a.value = N, c.value = !0, i(N);
    } catch (N) {
      if (h.value = N, s(N), d)
        throw N;
    } finally {
      f.value = !1;
    }
    return a.value;
  }
  r && g(o);
  const m = {
    state: a,
    isReady: c,
    isLoading: f,
    error: h,
    execute: g
  };
  function v() {
    return new Promise((_, b) => {
      dr(f).toBe(!1).then(() => _(m)).catch(b);
    });
  }
  return {
    ...m,
    then(_, b) {
      return v().then(_, b);
    }
  };
}
function B(e, t) {
  t = t || {};
  const n = [...Object.keys(t), "__Vue"], r = [...Object.values(t), Hn];
  try {
    return new Function(...n, `return (${e})`)(...r);
  } catch (o) {
    throw new Error(o + " in function code: " + e);
  }
}
function gr(e) {
  if (e.startsWith(":")) {
    e = e.slice(1);
    try {
      return B(e);
    } catch (t) {
      throw new Error(t + " in function code: " + e);
    }
  }
}
function Zt(e) {
  return e.constructor.name === "AsyncFunction";
}
class mr {
  toString() {
    return "";
  }
}
const we = new mr();
function be(e) {
  return qt(e) === we;
}
function vr(e) {
  return Array.isArray(e) && e[0] === "bind";
}
function yr(e) {
  return e[1];
}
function en(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...s] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + s[0];
      case "~+":
        return s[0] + e;
    }
  }
  const r = tn(t, n);
  return e[r];
}
function tn(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      if (!t)
        throw new Error("No bindable function provided");
      return t(r[0]);
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function nn(e, t, n) {
  return t.reduce(
    (r, o) => en(r, o, n),
    e
  );
}
function rn(e, t, n, r) {
  t.reduce((o, s, i) => {
    if (i === t.length - 1)
      o[tn(s, r)] = n;
    else
      return en(o, s, r);
  }, e);
}
function Er(e, t, n) {
  const { paths: r, getBindableValueFn: o } = t, { paths: s, getBindableValueFn: i } = t;
  return r === void 0 || r.length === 0 ? e : ie(() => ({
    get() {
      try {
        return nn(
          Je(e),
          r,
          o
        );
      } catch {
        return;
      }
    },
    set(u) {
      rn(
        Je(e),
        s || r,
        u,
        i
      );
    }
  }));
}
function ht(e) {
  return ie((t, n) => ({
    get() {
      return t(), e;
    },
    set(r) {
      !be(e) && JSON.stringify(r) === JSON.stringify(e) || (e = r, n());
    }
  }));
}
function _r(e, t) {
  const { deepCompare: n = !1 } = e;
  return n ? ht(e.value) : J(e.value);
}
function wr(e, t, n) {
  const { bind: r = {}, code: o, const: s = [] } = e, i = Object.values(r).map((a, c) => s[c] === 1 ? a : t.getVueRefObject(a));
  if (Zt(new Function(o)))
    return hr(
      async () => {
        const a = Object.fromEntries(
          Object.keys(r).map((c, f) => [c, i[f]])
        );
        return await B(o, a)();
      },
      null,
      { lazy: !0 }
    );
  const u = Object.fromEntries(
    Object.keys(r).map((a, c) => [a, i[c]])
  ), l = B(o, u);
  return W(l);
}
function br(e) {
  const { init: t, deepEqOnInput: n } = e;
  return n === void 0 ? G(t ?? we) : ht(t ?? we);
}
function Rr(e, t, n) {
  const {
    inputs: r = [],
    code: o,
    slient: s,
    data: i,
    asyncInit: u = null,
    deepEqOnInput: l = 0
  } = e, d = s || Array(r.length).fill(0), a = i || Array(r.length).fill(0), c = r.filter((v, _) => d[_] === 0 && a[_] === 0).map((v) => t.getVueRefObject(v));
  function f() {
    return r.map(
      (v, _) => a[_] === 1 ? v : t.getValue(v)
    );
  }
  const h = B(o), g = l === 0 ? G(we) : ht(we), m = { immediate: !0, deep: !0 };
  return Zt(h) ? (g.value = u, K(
    c,
    async () => {
      f().some(be) || (g.value = await h(...f()));
    },
    m
  )) : K(
    c,
    () => {
      const v = f();
      v.some(be) || (g.value = h(...v));
    },
    m
  ), Kn(g);
}
function Pr(e) {
  return e.tag === "vfor";
}
function Sr(e) {
  return e.tag === "vif";
}
function Or(e) {
  return e.tag === "match";
}
function on(e) {
  return !("type" in e);
}
function kr(e) {
  return "type" in e && e.type === "rp";
}
function pt(e) {
  return "sid" in e && "id" in e;
}
class Nr extends Map {
  constructor(t) {
    super(), this.factory = t;
  }
  getOrDefault(t) {
    if (!this.has(t)) {
      const n = this.factory();
      return this.set(t, n), n;
    }
    return super.get(t);
  }
}
function sn(e) {
  return new Nr(e);
}
class Vr {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: s } = t, i = Ye().webServerInfo, u = s !== void 0 ? { key: s } : {}, l = r === "sync" ? i.event_url : i.event_async_url;
    let d = {};
    const a = await fetch(l, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        bind: n,
        hKey: o,
        ...u,
        page: Ce(),
        ...d
      })
    });
    if (!a.ok)
      throw new Error(`HTTP error! status: ${a.status}`);
    return await a.json();
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = Ye().webServerInfo, s = n === "sync" ? o.watch_url : o.watch_async_url, i = t.getServerInputs(), u = {
      key: r,
      input: i,
      page: Ce()
    };
    return await (await fetch(s, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(u)
    })).json();
  }
}
class Cr {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: s } = t, i = s !== void 0 ? { key: s } : {};
    let u = {};
    const l = {
      bind: n,
      fType: r,
      hKey: o,
      ...i,
      page: Ce(),
      ...u
    };
    return await window.pywebview.api.event_call(l);
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = t.getServerInputs(), s = {
      key: r,
      input: o,
      fType: n,
      page: Ce()
    };
    return await window.pywebview.api.watch_call(s);
  }
}
let tt;
function Ir(e) {
  switch (e) {
    case "web":
      tt = new Vr();
      break;
    case "webview":
      tt = new Cr();
      break;
  }
}
function an() {
  return tt;
}
var H = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.EventContext = 1] = "EventContext", e[e.Data = 2] = "Data", e[e.JsFn = 3] = "JsFn", e))(H || {}), nt = /* @__PURE__ */ ((e) => (e.const = "c", e.ref = "r", e.range = "n", e))(nt || {}), ye = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.RouterAction = 1] = "RouterAction", e[e.ElementRefAction = 2] = "ElementRefAction", e))(ye || {});
function Ar(e, t) {
  const r = {
    ref: {
      id: t.id,
      sid: e
    },
    type: ye.Ref
  };
  return {
    ...t,
    immediate: !0,
    outputs: [r, ...t.outputs || []]
  };
}
function cn(e) {
  const { config: t, varGetter: n } = e;
  if (!t)
    return {
      run: () => {
      },
      tryReset: () => {
      }
    };
  const r = t.map((i) => {
    const u = n.getVueRefObject(i.target);
    return i.type === "const" ? {
      refObj: u,
      preValue: u.value,
      newValue: i.value,
      reset: !0
    } : $r(u, i, n);
  });
  return {
    run: () => {
      r.forEach((i) => {
        i.newValue !== i.preValue && (i.refObj.value = i.newValue);
      });
    },
    tryReset: () => {
      r.forEach((i) => {
        i.reset && (i.refObj.value = i.preValue);
      });
    }
  };
}
function $r(e, t, n) {
  const r = B(t.code), o = t.inputs.map((s) => n.getValue(s));
  return {
    refObj: e,
    preValue: e.value,
    reset: t.reset ?? !0,
    newValue: r(...o)
  };
}
function Rt(e) {
  return e == null;
}
function xe(e, t, n) {
  if (Rt(t) || Rt(e.values))
    return;
  t = t;
  const r = e.values, o = e.types ?? Array.from({ length: t.length }).fill(0);
  t.forEach((s, i) => {
    const u = o[i];
    if (u === 1)
      return;
    if (s.type === ye.Ref) {
      if (u === 2) {
        r[i].forEach(([a, c]) => {
          const f = s.ref, h = {
            ...f,
            path: [...f.path ?? [], ...a]
          };
          n.updateValue(h, c);
        });
        return;
      }
      n.updateValue(s.ref, r[i]);
      return;
    }
    if (s.type === ye.RouterAction) {
      const d = r[i], a = n.getRouter()[d.fn];
      a(...d.args);
      return;
    }
    if (s.type === ye.ElementRefAction) {
      const d = s.ref, a = n.getVueRefObject(d).value, c = r[i], { method: f, args: h = [] } = c;
      a[f](...h);
      return;
    }
    const l = n.getVueRefObject(
      s.ref
    );
    l.value = r[i];
  });
}
function xr(e) {
  const { watchConfigs: t, computedConfigs: n, varMapGetter: r, sid: o } = e;
  return new Tr(t, n, r, o);
}
class Tr {
  constructor(t, n, r, o) {
    $(this, "taskQueue", []);
    $(this, "id2TaskMap", /* @__PURE__ */ new Map());
    $(this, "input2TaskIdMap", sn(() => []));
    this.varMapGetter = r;
    const s = [], i = (u) => {
      var d;
      const l = new Dr(u, r);
      return this.id2TaskMap.set(l.id, l), (d = u.inputs) == null || d.forEach((a, c) => {
        var h, g;
        if (((h = u.data) == null ? void 0 : h[c]) === 0 && ((g = u.slient) == null ? void 0 : g[c]) === 0) {
          if (!on(a))
            throw new Error("Non-var input bindings are not supported.");
          const m = `${a.sid}-${a.id}`;
          this.input2TaskIdMap.getOrDefault(m).push(l.id);
        }
      }), l;
    };
    t == null || t.forEach((u) => {
      const l = i(u);
      s.push(l);
    }), n == null || n.forEach((u) => {
      const l = i(
        Ar(o, u)
      );
      s.push(l);
    }), s.forEach((u) => {
      const {
        deep: l = !0,
        once: d,
        flush: a,
        immediate: c = !0
      } = u.watchConfig, f = {
        immediate: c,
        deep: l,
        once: d,
        flush: a
      }, h = this._getWatchTargets(u);
      K(
        h,
        (g) => {
          g.some(be) || (u.modify = !0, this.taskQueue.push(new jr(u)), this._scheduleNextTick());
        },
        f
      );
    });
  }
  _getWatchTargets(t) {
    if (!t.watchConfig.inputs)
      return [];
    const n = t.slientInputs, r = t.constDataInputs;
    return t.watchConfig.inputs.filter(
      (s, i) => !r[i] && !n[i]
    ).map((s) => this.varMapGetter.getVueRefObject(s));
  }
  _scheduleNextTick() {
    ke(() => this._runAllTasks());
  }
  _runAllTasks() {
    const t = this.taskQueue.slice();
    this.taskQueue.length = 0, this._setTaskNodeRelations(t), t.forEach((n) => {
      n.run();
    });
  }
  _setTaskNodeRelations(t) {
    t.forEach((n) => {
      const r = this._findNextNodes(n, t);
      n.appendNextNodes(...r), r.forEach((o) => {
        o.appendPrevNodes(n);
      });
    });
  }
  _findNextNodes(t, n) {
    const r = t.watchTask.watchConfig.outputs;
    if (r && r.length <= 0)
      return [];
    const o = this._getCalculatorTasksByOutput(
      t.watchTask.watchConfig.outputs
    );
    return n.filter(
      (s) => o.has(s.watchTask.id) && s.watchTask.id !== t.watchTask.id
    );
  }
  _getCalculatorTasksByOutput(t) {
    const n = /* @__PURE__ */ new Set();
    return t == null || t.forEach((r) => {
      if (!pt(r.ref))
        throw new Error("Non-var output bindings are not supported.");
      const { sid: o, id: s } = r.ref, i = `${o}-${s}`;
      (this.input2TaskIdMap.get(i) || []).forEach((l) => n.add(l));
    }), n;
  }
}
class Dr {
  constructor(t, n) {
    $(this, "modify", !0);
    $(this, "_running", !1);
    $(this, "id");
    $(this, "_runningPromise", null);
    $(this, "_runningPromiseResolve", null);
    $(this, "_inputInfos");
    this.watchConfig = t, this.varMapGetter = n, this.id = Symbol(t.debug), this._inputInfos = this.createInputInfos();
  }
  createInputInfos() {
    const { inputs: t = [] } = this.watchConfig, n = this.watchConfig.data || Array.from({ length: t.length }).fill(0), r = this.watchConfig.slient || Array.from({ length: t.length }).fill(0);
    return {
      const_data: n,
      slients: r
    };
  }
  get slientInputs() {
    return this._inputInfos.slients;
  }
  get constDataInputs() {
    return this._inputInfos.const_data;
  }
  getServerInputs() {
    const { const_data: t } = this._inputInfos;
    return this.watchConfig.inputs ? this.watchConfig.inputs.map((n, r) => t[r] === 0 ? this.varMapGetter.getValue(n) : n) : [];
  }
  get running() {
    return this._running;
  }
  get runningPromise() {
    return this._runningPromise;
  }
  /**
   * setRunning
   */
  setRunning() {
    this._running = !0, this._runningPromise = new Promise((t) => {
      this._runningPromiseResolve = t;
    });
  }
  /**
   * taskDone
   */
  taskDone() {
    this._running = !1, this._runningPromiseResolve && (this._runningPromiseResolve(), this._runningPromiseResolve = null);
  }
}
class jr {
  /**
   *
   */
  constructor(t) {
    $(this, "prevNodes", []);
    $(this, "nextNodes", []);
    $(this, "_runningPrev", !1);
    this.watchTask = t;
  }
  /**
   * appendPrevNodes
   */
  appendPrevNodes(...t) {
    this.prevNodes.push(...t);
  }
  /**
   *
   */
  appendNextNodes(...t) {
    this.nextNodes.push(...t);
  }
  /**
   * hasNextNodes
   */
  hasNextNodes() {
    return this.nextNodes.length > 0;
  }
  /**
   * run
   */
  async run() {
    if (this.prevNodes.length > 0 && !this._runningPrev)
      try {
        this._runningPrev = !0, await Promise.all(this.prevNodes.map((t) => t.run()));
      } finally {
        this._runningPrev = !1;
      }
    if (this.watchTask.running) {
      await this.watchTask.runningPromise;
      return;
    }
    if (this.watchTask.modify) {
      this.watchTask.modify = !1, this.watchTask.setRunning();
      try {
        await Mr(this.watchTask);
      } finally {
        this.watchTask.taskDone();
      }
    }
  }
}
async function Mr(e) {
  const { varMapGetter: t } = e, { outputs: n, preSetup: r } = e.watchConfig, o = cn({
    config: r,
    varGetter: t
  });
  try {
    o.run(), e.taskDone();
    const s = await an().watchSend(e);
    if (!s)
      return;
    xe(s, n, t);
  } finally {
    o.tryReset();
  }
}
function Pt(e, t) {
  Object.entries(e).forEach(([n, r]) => t(r, n));
}
function Te(e, t) {
  return un(e, {
    valueFn: t
  });
}
function un(e, t) {
  const { valueFn: n, keyFn: r } = t;
  return Object.fromEntries(
    Object.entries(e).map(([o, s], i) => [
      r ? r(o, s) : o,
      n(s, o, i)
    ])
  );
}
function Wr(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...s] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + s[0];
      case "~+":
        return s[0] + e;
    }
  }
  const r = Br(t);
  return e[r];
}
function Br(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      throw new Error("No bindable function provided");
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function Lr(e, t, n) {
  return t.reduce(
    (r, o) => Wr(r, o),
    e
  );
}
function Fr(e, t) {
  return t ? t.reduce((n, r) => n[r], e) : e;
}
const Ur = window.structuredClone || ((e) => JSON.parse(JSON.stringify(e)));
function ln(e) {
  return typeof e == "function" ? e : Ur(qt(e));
}
function Gr(e, t) {
  const {
    on: n,
    code: r,
    immediate: o,
    deep: s,
    once: i,
    flush: u,
    bind: l = {},
    onData: d,
    bindData: a
  } = e, c = d || Array.from({ length: n.length }).fill(0), f = a || Array.from({ length: Object.keys(l).length }).fill(0), h = Te(
    l,
    (v, _, b) => f[b] === 0 ? t.getVueRefObject(v) : v
  ), g = B(r, h), m = n.length === 1 ? St(c[0] === 1, n[0], t) : n.map(
    (v, _) => St(c[_] === 1, v, t)
  );
  return K(m, g, { immediate: o, deep: s, once: i, flush: u });
}
function St(e, t, n) {
  return e ? () => t : n.getVueRefObject(t);
}
function Hr(e, t) {
  const {
    inputs: n = [],
    outputs: r,
    slient: o,
    data: s,
    code: i,
    immediate: u = !0,
    deep: l,
    once: d,
    flush: a
  } = e, c = o || Array.from({ length: n.length }).fill(0), f = s || Array.from({ length: n.length }).fill(0), h = B(i), g = n.filter((v, _) => c[_] === 0 && f[_] === 0).map((v) => t.getVueRefObject(v));
  function m() {
    return n.map((v, _) => f[_] === 0 ? ln(t.getValue(v)) : v);
  }
  K(
    g,
    () => {
      let v = h(...m());
      if (!r)
        return;
      const b = r.length === 1 ? [v] : v, R = b.map((N) => N === void 0 ? 1 : 0);
      xe(
        {
          values: b,
          types: R
        },
        r,
        t
      );
    },
    { immediate: u, deep: l, once: d, flush: a }
  );
}
const rt = sn(() => Symbol());
function Kr(e, t) {
  const n = e.sid, r = rt.getOrDefault(n);
  rt.set(n, r), ae(r, t);
}
function zr(e) {
  const t = rt.get(e);
  return z(t);
}
function qr() {
  return fn().__VUE_DEVTOOLS_GLOBAL_HOOK__;
}
function fn() {
  return typeof navigator < "u" && typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : {};
}
const Qr = typeof Proxy == "function", Jr = "devtools-plugin:setup", Yr = "plugin:settings:set";
let oe, ot;
function Xr() {
  var e;
  return oe !== void 0 || (typeof window < "u" && window.performance ? (oe = !0, ot = window.performance) : typeof globalThis < "u" && (!((e = globalThis.perf_hooks) === null || e === void 0) && e.performance) ? (oe = !0, ot = globalThis.perf_hooks.performance) : oe = !1), oe;
}
function Zr() {
  return Xr() ? ot.now() : Date.now();
}
class eo {
  constructor(t, n) {
    this.target = null, this.targetQueue = [], this.onQueue = [], this.plugin = t, this.hook = n;
    const r = {};
    if (t.settings)
      for (const i in t.settings) {
        const u = t.settings[i];
        r[i] = u.defaultValue;
      }
    const o = `__vue-devtools-plugin-settings__${t.id}`;
    let s = Object.assign({}, r);
    try {
      const i = localStorage.getItem(o), u = JSON.parse(i);
      Object.assign(s, u);
    } catch {
    }
    this.fallbacks = {
      getSettings() {
        return s;
      },
      setSettings(i) {
        try {
          localStorage.setItem(o, JSON.stringify(i));
        } catch {
        }
        s = i;
      },
      now() {
        return Zr();
      }
    }, n && n.on(Yr, (i, u) => {
      i === this.plugin.id && this.fallbacks.setSettings(u);
    }), this.proxiedOn = new Proxy({}, {
      get: (i, u) => this.target ? this.target.on[u] : (...l) => {
        this.onQueue.push({
          method: u,
          args: l
        });
      }
    }), this.proxiedTarget = new Proxy({}, {
      get: (i, u) => this.target ? this.target[u] : u === "on" ? this.proxiedOn : Object.keys(this.fallbacks).includes(u) ? (...l) => (this.targetQueue.push({
        method: u,
        args: l,
        resolve: () => {
        }
      }), this.fallbacks[u](...l)) : (...l) => new Promise((d) => {
        this.targetQueue.push({
          method: u,
          args: l,
          resolve: d
        });
      })
    });
  }
  async setRealTarget(t) {
    this.target = t;
    for (const n of this.onQueue)
      this.target.on[n.method](...n.args);
    for (const n of this.targetQueue)
      n.resolve(await this.target[n.method](...n.args));
  }
}
function to(e, t) {
  const n = e, r = fn(), o = qr(), s = Qr && n.enableEarlyProxy;
  if (o && (r.__VUE_DEVTOOLS_PLUGIN_API_AVAILABLE__ || !s))
    o.emit(Jr, e, t);
  else {
    const i = s ? new eo(n, o) : null;
    (r.__VUE_DEVTOOLS_PLUGINS__ = r.__VUE_DEVTOOLS_PLUGINS__ || []).push({
      pluginDescriptor: n,
      setupFn: t,
      proxy: i
    }), i && t(i.proxiedTarget);
  }
}
var P = {};
const Q = typeof document < "u";
function dn(e) {
  return typeof e == "object" || "displayName" in e || "props" in e || "__vccOpts" in e;
}
function no(e) {
  return e.__esModule || e[Symbol.toStringTag] === "Module" || // support CF with dynamic imports that do not
  // add the Module string tag
  e.default && dn(e.default);
}
const V = Object.assign;
function He(e, t) {
  const n = {};
  for (const r in t) {
    const o = t[r];
    n[r] = L(o) ? o.map(e) : e(o);
  }
  return n;
}
const Ee = () => {
}, L = Array.isArray;
function S(e) {
  const t = Array.from(arguments).slice(1);
  console.warn.apply(console, ["[Vue Router warn]: " + e].concat(t));
}
const hn = /#/g, ro = /&/g, oo = /\//g, so = /=/g, io = /\?/g, pn = /\+/g, ao = /%5B/g, co = /%5D/g, gn = /%5E/g, uo = /%60/g, mn = /%7B/g, lo = /%7C/g, vn = /%7D/g, fo = /%20/g;
function gt(e) {
  return encodeURI("" + e).replace(lo, "|").replace(ao, "[").replace(co, "]");
}
function ho(e) {
  return gt(e).replace(mn, "{").replace(vn, "}").replace(gn, "^");
}
function st(e) {
  return gt(e).replace(pn, "%2B").replace(fo, "+").replace(hn, "%23").replace(ro, "%26").replace(uo, "`").replace(mn, "{").replace(vn, "}").replace(gn, "^");
}
function po(e) {
  return st(e).replace(so, "%3D");
}
function go(e) {
  return gt(e).replace(hn, "%23").replace(io, "%3F");
}
function mo(e) {
  return e == null ? "" : go(e).replace(oo, "%2F");
}
function ce(e) {
  try {
    return decodeURIComponent("" + e);
  } catch {
    P.NODE_ENV !== "production" && S(`Error decoding "${e}". Using original value`);
  }
  return "" + e;
}
const vo = /\/$/, yo = (e) => e.replace(vo, "");
function Ke(e, t, n = "/") {
  let r, o = {}, s = "", i = "";
  const u = t.indexOf("#");
  let l = t.indexOf("?");
  return u < l && u >= 0 && (l = -1), l > -1 && (r = t.slice(0, l), s = t.slice(l + 1, u > -1 ? u : t.length), o = e(s)), u > -1 && (r = r || t.slice(0, u), i = t.slice(u, t.length)), r = wo(r ?? t, n), {
    fullPath: r + (s && "?") + s + i,
    path: r,
    query: o,
    hash: ce(i)
  };
}
function Eo(e, t) {
  const n = t.query ? e(t.query) : "";
  return t.path + (n && "?") + n + (t.hash || "");
}
function Ot(e, t) {
  return !t || !e.toLowerCase().startsWith(t.toLowerCase()) ? e : e.slice(t.length) || "/";
}
function kt(e, t, n) {
  const r = t.matched.length - 1, o = n.matched.length - 1;
  return r > -1 && r === o && Z(t.matched[r], n.matched[o]) && yn(t.params, n.params) && e(t.query) === e(n.query) && t.hash === n.hash;
}
function Z(e, t) {
  return (e.aliasOf || e) === (t.aliasOf || t);
}
function yn(e, t) {
  if (Object.keys(e).length !== Object.keys(t).length)
    return !1;
  for (const n in e)
    if (!_o(e[n], t[n]))
      return !1;
  return !0;
}
function _o(e, t) {
  return L(e) ? Nt(e, t) : L(t) ? Nt(t, e) : e === t;
}
function Nt(e, t) {
  return L(t) ? e.length === t.length && e.every((n, r) => n === t[r]) : e.length === 1 && e[0] === t;
}
function wo(e, t) {
  if (e.startsWith("/"))
    return e;
  if (P.NODE_ENV !== "production" && !t.startsWith("/"))
    return S(`Cannot resolve a relative location without an absolute path. Trying to resolve "${e}" from "${t}". It should look like "/${t}".`), e;
  if (!e)
    return t;
  const n = t.split("/"), r = e.split("/"), o = r[r.length - 1];
  (o === ".." || o === ".") && r.push("");
  let s = n.length - 1, i, u;
  for (i = 0; i < r.length; i++)
    if (u = r[i], u !== ".")
      if (u === "..")
        s > 1 && s--;
      else
        break;
  return n.slice(0, s).join("/") + "/" + r.slice(i).join("/");
}
const Y = {
  path: "/",
  // TODO: could we use a symbol in the future?
  name: void 0,
  params: {},
  query: {},
  hash: "",
  fullPath: "/",
  matched: [],
  meta: {},
  redirectedFrom: void 0
};
var ue;
(function(e) {
  e.pop = "pop", e.push = "push";
})(ue || (ue = {}));
var te;
(function(e) {
  e.back = "back", e.forward = "forward", e.unknown = "";
})(te || (te = {}));
const ze = "";
function En(e) {
  if (!e)
    if (Q) {
      const t = document.querySelector("base");
      e = t && t.getAttribute("href") || "/", e = e.replace(/^\w+:\/\/[^\/]+/, "");
    } else
      e = "/";
  return e[0] !== "/" && e[0] !== "#" && (e = "/" + e), yo(e);
}
const bo = /^[^#]+#/;
function _n(e, t) {
  return e.replace(bo, "#") + t;
}
function Ro(e, t) {
  const n = document.documentElement.getBoundingClientRect(), r = e.getBoundingClientRect();
  return {
    behavior: t.behavior,
    left: r.left - n.left - (t.left || 0),
    top: r.top - n.top - (t.top || 0)
  };
}
const De = () => ({
  left: window.scrollX,
  top: window.scrollY
});
function Po(e) {
  let t;
  if ("el" in e) {
    const n = e.el, r = typeof n == "string" && n.startsWith("#");
    if (P.NODE_ENV !== "production" && typeof e.el == "string" && (!r || !document.getElementById(e.el.slice(1))))
      try {
        const s = document.querySelector(e.el);
        if (r && s) {
          S(`The selector "${e.el}" should be passed as "el: document.querySelector('${e.el}')" because it starts with "#".`);
          return;
        }
      } catch {
        S(`The selector "${e.el}" is invalid. If you are using an id selector, make sure to escape it. You can find more information about escaping characters in selectors at https://mathiasbynens.be/notes/css-escapes or use CSS.escape (https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape).`);
        return;
      }
    const o = typeof n == "string" ? r ? document.getElementById(n.slice(1)) : document.querySelector(n) : n;
    if (!o) {
      P.NODE_ENV !== "production" && S(`Couldn't find element using selector "${e.el}" returned by scrollBehavior.`);
      return;
    }
    t = Ro(o, e);
  } else
    t = e;
  "scrollBehavior" in document.documentElement.style ? window.scrollTo(t) : window.scrollTo(t.left != null ? t.left : window.scrollX, t.top != null ? t.top : window.scrollY);
}
function Vt(e, t) {
  return (history.state ? history.state.position - t : -1) + e;
}
const it = /* @__PURE__ */ new Map();
function So(e, t) {
  it.set(e, t);
}
function Oo(e) {
  const t = it.get(e);
  return it.delete(e), t;
}
let ko = () => location.protocol + "//" + location.host;
function wn(e, t) {
  const { pathname: n, search: r, hash: o } = t, s = e.indexOf("#");
  if (s > -1) {
    let u = o.includes(e.slice(s)) ? e.slice(s).length : 1, l = o.slice(u);
    return l[0] !== "/" && (l = "/" + l), Ot(l, "");
  }
  return Ot(n, e) + r + o;
}
function No(e, t, n, r) {
  let o = [], s = [], i = null;
  const u = ({ state: f }) => {
    const h = wn(e, location), g = n.value, m = t.value;
    let v = 0;
    if (f) {
      if (n.value = h, t.value = f, i && i === g) {
        i = null;
        return;
      }
      v = m ? f.position - m.position : 0;
    } else
      r(h);
    o.forEach((_) => {
      _(n.value, g, {
        delta: v,
        type: ue.pop,
        direction: v ? v > 0 ? te.forward : te.back : te.unknown
      });
    });
  };
  function l() {
    i = n.value;
  }
  function d(f) {
    o.push(f);
    const h = () => {
      const g = o.indexOf(f);
      g > -1 && o.splice(g, 1);
    };
    return s.push(h), h;
  }
  function a() {
    const { history: f } = window;
    f.state && f.replaceState(V({}, f.state, { scroll: De() }), "");
  }
  function c() {
    for (const f of s)
      f();
    s = [], window.removeEventListener("popstate", u), window.removeEventListener("beforeunload", a);
  }
  return window.addEventListener("popstate", u), window.addEventListener("beforeunload", a, {
    passive: !0
  }), {
    pauseListeners: l,
    listen: d,
    destroy: c
  };
}
function Ct(e, t, n, r = !1, o = !1) {
  return {
    back: e,
    current: t,
    forward: n,
    replaced: r,
    position: window.history.length,
    scroll: o ? De() : null
  };
}
function Vo(e) {
  const { history: t, location: n } = window, r = {
    value: wn(e, n)
  }, o = { value: t.state };
  o.value || s(r.value, {
    back: null,
    current: r.value,
    forward: null,
    // the length is off by one, we need to decrease it
    position: t.length - 1,
    replaced: !0,
    // don't add a scroll as the user may have an anchor, and we want
    // scrollBehavior to be triggered without a saved position
    scroll: null
  }, !0);
  function s(l, d, a) {
    const c = e.indexOf("#"), f = c > -1 ? (n.host && document.querySelector("base") ? e : e.slice(c)) + l : ko() + e + l;
    try {
      t[a ? "replaceState" : "pushState"](d, "", f), o.value = d;
    } catch (h) {
      P.NODE_ENV !== "production" ? S("Error with push/replace State", h) : console.error(h), n[a ? "replace" : "assign"](f);
    }
  }
  function i(l, d) {
    const a = V({}, t.state, Ct(
      o.value.back,
      // keep back and forward entries but override current position
      l,
      o.value.forward,
      !0
    ), d, { position: o.value.position });
    s(l, a, !0), r.value = l;
  }
  function u(l, d) {
    const a = V(
      {},
      // use current history state to gracefully handle a wrong call to
      // history.replaceState
      // https://github.com/vuejs/router/issues/366
      o.value,
      t.state,
      {
        forward: l,
        scroll: De()
      }
    );
    P.NODE_ENV !== "production" && !t.state && S(`history.state seems to have been manually replaced without preserving the necessary values. Make sure to preserve existing history state if you are manually calling history.replaceState:

history.replaceState(history.state, '', url)

You can find more information at https://router.vuejs.org/guide/migration/#Usage-of-history-state`), s(a.current, a, !0);
    const c = V({}, Ct(r.value, l, null), { position: a.position + 1 }, d);
    s(l, c, !1), r.value = l;
  }
  return {
    location: r,
    state: o,
    push: u,
    replace: i
  };
}
function bn(e) {
  e = En(e);
  const t = Vo(e), n = No(e, t.state, t.location, t.replace);
  function r(s, i = !0) {
    i || n.pauseListeners(), history.go(s);
  }
  const o = V({
    // it's overridden right after
    location: "",
    base: e,
    go: r,
    createHref: _n.bind(null, e)
  }, t, n);
  return Object.defineProperty(o, "location", {
    enumerable: !0,
    get: () => t.location.value
  }), Object.defineProperty(o, "state", {
    enumerable: !0,
    get: () => t.state.value
  }), o;
}
function Co(e = "") {
  let t = [], n = [ze], r = 0;
  e = En(e);
  function o(u) {
    r++, r !== n.length && n.splice(r), n.push(u);
  }
  function s(u, l, { direction: d, delta: a }) {
    const c = {
      direction: d,
      delta: a,
      type: ue.pop
    };
    for (const f of t)
      f(u, l, c);
  }
  const i = {
    // rewritten by Object.defineProperty
    location: ze,
    // TODO: should be kept in queue
    state: {},
    base: e,
    createHref: _n.bind(null, e),
    replace(u) {
      n.splice(r--, 1), o(u);
    },
    push(u, l) {
      o(u);
    },
    listen(u) {
      return t.push(u), () => {
        const l = t.indexOf(u);
        l > -1 && t.splice(l, 1);
      };
    },
    destroy() {
      t = [], n = [ze], r = 0;
    },
    go(u, l = !0) {
      const d = this.location, a = (
        // we are considering delta === 0 going forward, but in abstract mode
        // using 0 for the delta doesn't make sense like it does in html5 where
        // it reloads the page
        u < 0 ? te.back : te.forward
      );
      r = Math.max(0, Math.min(r + u, n.length - 1)), l && s(this.location, d, {
        direction: a,
        delta: u
      });
    }
  };
  return Object.defineProperty(i, "location", {
    enumerable: !0,
    get: () => n[r]
  }), i;
}
function Io(e) {
  return e = location.host ? e || location.pathname + location.search : "", e.includes("#") || (e += "#"), P.NODE_ENV !== "production" && !e.endsWith("#/") && !e.endsWith("#") && S(`A hash base must end with a "#":
"${e}" should be "${e.replace(/#.*$/, "#")}".`), bn(e);
}
function Ie(e) {
  return typeof e == "string" || e && typeof e == "object";
}
function Rn(e) {
  return typeof e == "string" || typeof e == "symbol";
}
const at = Symbol(P.NODE_ENV !== "production" ? "navigation failure" : "");
var It;
(function(e) {
  e[e.aborted = 4] = "aborted", e[e.cancelled = 8] = "cancelled", e[e.duplicated = 16] = "duplicated";
})(It || (It = {}));
const Ao = {
  1({ location: e, currentLocation: t }) {
    return `No match for
 ${JSON.stringify(e)}${t ? `
while being at
` + JSON.stringify(t) : ""}`;
  },
  2({ from: e, to: t }) {
    return `Redirected from "${e.fullPath}" to "${xo(t)}" via a navigation guard.`;
  },
  4({ from: e, to: t }) {
    return `Navigation aborted from "${e.fullPath}" to "${t.fullPath}" via a navigation guard.`;
  },
  8({ from: e, to: t }) {
    return `Navigation cancelled from "${e.fullPath}" to "${t.fullPath}" with a new navigation.`;
  },
  16({ from: e, to: t }) {
    return `Avoided redundant navigation to current location: "${e.fullPath}".`;
  }
};
function le(e, t) {
  return P.NODE_ENV !== "production" ? V(new Error(Ao[e](t)), {
    type: e,
    [at]: !0
  }, t) : V(new Error(), {
    type: e,
    [at]: !0
  }, t);
}
function q(e, t) {
  return e instanceof Error && at in e && (t == null || !!(e.type & t));
}
const $o = ["params", "query", "hash"];
function xo(e) {
  if (typeof e == "string")
    return e;
  if (e.path != null)
    return e.path;
  const t = {};
  for (const n of $o)
    n in e && (t[n] = e[n]);
  return JSON.stringify(t, null, 2);
}
const At = "[^/]+?", To = {
  sensitive: !1,
  strict: !1,
  start: !0,
  end: !0
}, Do = /[.+*?^${}()[\]/\\]/g;
function jo(e, t) {
  const n = V({}, To, t), r = [];
  let o = n.start ? "^" : "";
  const s = [];
  for (const d of e) {
    const a = d.length ? [] : [
      90
      /* PathScore.Root */
    ];
    n.strict && !d.length && (o += "/");
    for (let c = 0; c < d.length; c++) {
      const f = d[c];
      let h = 40 + (n.sensitive ? 0.25 : 0);
      if (f.type === 0)
        c || (o += "/"), o += f.value.replace(Do, "\\$&"), h += 40;
      else if (f.type === 1) {
        const { value: g, repeatable: m, optional: v, regexp: _ } = f;
        s.push({
          name: g,
          repeatable: m,
          optional: v
        });
        const b = _ || At;
        if (b !== At) {
          h += 10;
          try {
            new RegExp(`(${b})`);
          } catch (N) {
            throw new Error(`Invalid custom RegExp for param "${g}" (${b}): ` + N.message);
          }
        }
        let R = m ? `((?:${b})(?:/(?:${b}))*)` : `(${b})`;
        c || (R = // avoid an optional / if there are more segments e.g. /:p?-static
        // or /:p?-:p2
        v && d.length < 2 ? `(?:/${R})` : "/" + R), v && (R += "?"), o += R, h += 20, v && (h += -8), m && (h += -20), b === ".*" && (h += -50);
      }
      a.push(h);
    }
    r.push(a);
  }
  if (n.strict && n.end) {
    const d = r.length - 1;
    r[d][r[d].length - 1] += 0.7000000000000001;
  }
  n.strict || (o += "/?"), n.end ? o += "$" : n.strict && !o.endsWith("/") && (o += "(?:/|$)");
  const i = new RegExp(o, n.sensitive ? "" : "i");
  function u(d) {
    const a = d.match(i), c = {};
    if (!a)
      return null;
    for (let f = 1; f < a.length; f++) {
      const h = a[f] || "", g = s[f - 1];
      c[g.name] = h && g.repeatable ? h.split("/") : h;
    }
    return c;
  }
  function l(d) {
    let a = "", c = !1;
    for (const f of e) {
      (!c || !a.endsWith("/")) && (a += "/"), c = !1;
      for (const h of f)
        if (h.type === 0)
          a += h.value;
        else if (h.type === 1) {
          const { value: g, repeatable: m, optional: v } = h, _ = g in d ? d[g] : "";
          if (L(_) && !m)
            throw new Error(`Provided param "${g}" is an array but it is not repeatable (* or + modifiers)`);
          const b = L(_) ? _.join("/") : _;
          if (!b)
            if (v)
              f.length < 2 && (a.endsWith("/") ? a = a.slice(0, -1) : c = !0);
            else
              throw new Error(`Missing required param "${g}"`);
          a += b;
        }
    }
    return a || "/";
  }
  return {
    re: i,
    score: r,
    keys: s,
    parse: u,
    stringify: l
  };
}
function Mo(e, t) {
  let n = 0;
  for (; n < e.length && n < t.length; ) {
    const r = t[n] - e[n];
    if (r)
      return r;
    n++;
  }
  return e.length < t.length ? e.length === 1 && e[0] === 80 ? -1 : 1 : e.length > t.length ? t.length === 1 && t[0] === 80 ? 1 : -1 : 0;
}
function Pn(e, t) {
  let n = 0;
  const r = e.score, o = t.score;
  for (; n < r.length && n < o.length; ) {
    const s = Mo(r[n], o[n]);
    if (s)
      return s;
    n++;
  }
  if (Math.abs(o.length - r.length) === 1) {
    if ($t(r))
      return 1;
    if ($t(o))
      return -1;
  }
  return o.length - r.length;
}
function $t(e) {
  const t = e[e.length - 1];
  return e.length > 0 && t[t.length - 1] < 0;
}
const Wo = {
  type: 0,
  value: ""
}, Bo = /[a-zA-Z0-9_]/;
function Lo(e) {
  if (!e)
    return [[]];
  if (e === "/")
    return [[Wo]];
  if (!e.startsWith("/"))
    throw new Error(P.NODE_ENV !== "production" ? `Route paths should start with a "/": "${e}" should be "/${e}".` : `Invalid path "${e}"`);
  function t(h) {
    throw new Error(`ERR (${n})/"${d}": ${h}`);
  }
  let n = 0, r = n;
  const o = [];
  let s;
  function i() {
    s && o.push(s), s = [];
  }
  let u = 0, l, d = "", a = "";
  function c() {
    d && (n === 0 ? s.push({
      type: 0,
      value: d
    }) : n === 1 || n === 2 || n === 3 ? (s.length > 1 && (l === "*" || l === "+") && t(`A repeatable param (${d}) must be alone in its segment. eg: '/:ids+.`), s.push({
      type: 1,
      value: d,
      regexp: a,
      repeatable: l === "*" || l === "+",
      optional: l === "*" || l === "?"
    })) : t("Invalid state to consume buffer"), d = "");
  }
  function f() {
    d += l;
  }
  for (; u < e.length; ) {
    if (l = e[u++], l === "\\" && n !== 2) {
      r = n, n = 4;
      continue;
    }
    switch (n) {
      case 0:
        l === "/" ? (d && c(), i()) : l === ":" ? (c(), n = 1) : f();
        break;
      case 4:
        f(), n = r;
        break;
      case 1:
        l === "(" ? n = 2 : Bo.test(l) ? f() : (c(), n = 0, l !== "*" && l !== "?" && l !== "+" && u--);
        break;
      case 2:
        l === ")" ? a[a.length - 1] == "\\" ? a = a.slice(0, -1) + l : n = 3 : a += l;
        break;
      case 3:
        c(), n = 0, l !== "*" && l !== "?" && l !== "+" && u--, a = "";
        break;
      default:
        t("Unknown state");
        break;
    }
  }
  return n === 2 && t(`Unfinished custom RegExp for param "${d}"`), c(), i(), o;
}
function Fo(e, t, n) {
  const r = jo(Lo(e.path), n);
  if (P.NODE_ENV !== "production") {
    const s = /* @__PURE__ */ new Set();
    for (const i of r.keys)
      s.has(i.name) && S(`Found duplicated params with name "${i.name}" for path "${e.path}". Only the last one will be available on "$route.params".`), s.add(i.name);
  }
  const o = V(r, {
    record: e,
    parent: t,
    // these needs to be populated by the parent
    children: [],
    alias: []
  });
  return t && !o.record.aliasOf == !t.record.aliasOf && t.children.push(o), o;
}
function Uo(e, t) {
  const n = [], r = /* @__PURE__ */ new Map();
  t = jt({ strict: !1, end: !0, sensitive: !1 }, t);
  function o(c) {
    return r.get(c);
  }
  function s(c, f, h) {
    const g = !h, m = Tt(c);
    P.NODE_ENV !== "production" && zo(m, f), m.aliasOf = h && h.record;
    const v = jt(t, c), _ = [m];
    if ("alias" in c) {
      const N = typeof c.alias == "string" ? [c.alias] : c.alias;
      for (const j of N)
        _.push(
          // we need to normalize again to ensure the `mods` property
          // being non enumerable
          Tt(V({}, m, {
            // this allows us to hold a copy of the `components` option
            // so that async components cache is hold on the original record
            components: h ? h.record.components : m.components,
            path: j,
            // we might be the child of an alias
            aliasOf: h ? h.record : m
            // the aliases are always of the same kind as the original since they
            // are defined on the same record
          }))
        );
    }
    let b, R;
    for (const N of _) {
      const { path: j } = N;
      if (f && j[0] !== "/") {
        const U = f.record.path, F = U[U.length - 1] === "/" ? "" : "/";
        N.path = f.record.path + (j && F + j);
      }
      if (P.NODE_ENV !== "production" && N.path === "*")
        throw new Error(`Catch all routes ("*") must now be defined using a param with a custom regexp.
See more at https://router.vuejs.org/guide/migration/#Removed-star-or-catch-all-routes.`);
      if (b = Fo(N, f, v), P.NODE_ENV !== "production" && f && j[0] === "/" && Qo(b, f), h ? (h.alias.push(b), P.NODE_ENV !== "production" && Ko(h, b)) : (R = R || b, R !== b && R.alias.push(b), g && c.name && !Dt(b) && (P.NODE_ENV !== "production" && qo(c, f), i(c.name))), Sn(b) && l(b), m.children) {
        const U = m.children;
        for (let F = 0; F < U.length; F++)
          s(U[F], b, h && h.children[F]);
      }
      h = h || b;
    }
    return R ? () => {
      i(R);
    } : Ee;
  }
  function i(c) {
    if (Rn(c)) {
      const f = r.get(c);
      f && (r.delete(c), n.splice(n.indexOf(f), 1), f.children.forEach(i), f.alias.forEach(i));
    } else {
      const f = n.indexOf(c);
      f > -1 && (n.splice(f, 1), c.record.name && r.delete(c.record.name), c.children.forEach(i), c.alias.forEach(i));
    }
  }
  function u() {
    return n;
  }
  function l(c) {
    const f = Jo(c, n);
    n.splice(f, 0, c), c.record.name && !Dt(c) && r.set(c.record.name, c);
  }
  function d(c, f) {
    let h, g = {}, m, v;
    if ("name" in c && c.name) {
      if (h = r.get(c.name), !h)
        throw le(1, {
          location: c
        });
      if (P.NODE_ENV !== "production") {
        const R = Object.keys(c.params || {}).filter((N) => !h.keys.find((j) => j.name === N));
        R.length && S(`Discarded invalid param(s) "${R.join('", "')}" when navigating. See https://github.com/vuejs/router/blob/main/packages/router/CHANGELOG.md#414-2022-08-22 for more details.`);
      }
      v = h.record.name, g = V(
        // paramsFromLocation is a new object
        xt(
          f.params,
          // only keep params that exist in the resolved location
          // only keep optional params coming from a parent record
          h.keys.filter((R) => !R.optional).concat(h.parent ? h.parent.keys.filter((R) => R.optional) : []).map((R) => R.name)
        ),
        // discard any existing params in the current location that do not exist here
        // #1497 this ensures better active/exact matching
        c.params && xt(c.params, h.keys.map((R) => R.name))
      ), m = h.stringify(g);
    } else if (c.path != null)
      m = c.path, P.NODE_ENV !== "production" && !m.startsWith("/") && S(`The Matcher cannot resolve relative paths but received "${m}". Unless you directly called \`matcher.resolve("${m}")\`, this is probably a bug in vue-router. Please open an issue at https://github.com/vuejs/router/issues/new/choose.`), h = n.find((R) => R.re.test(m)), h && (g = h.parse(m), v = h.record.name);
    else {
      if (h = f.name ? r.get(f.name) : n.find((R) => R.re.test(f.path)), !h)
        throw le(1, {
          location: c,
          currentLocation: f
        });
      v = h.record.name, g = V({}, f.params, c.params), m = h.stringify(g);
    }
    const _ = [];
    let b = h;
    for (; b; )
      _.unshift(b.record), b = b.parent;
    return {
      name: v,
      path: m,
      params: g,
      matched: _,
      meta: Ho(_)
    };
  }
  e.forEach((c) => s(c));
  function a() {
    n.length = 0, r.clear();
  }
  return {
    addRoute: s,
    resolve: d,
    removeRoute: i,
    clearRoutes: a,
    getRoutes: u,
    getRecordMatcher: o
  };
}
function xt(e, t) {
  const n = {};
  for (const r of t)
    r in e && (n[r] = e[r]);
  return n;
}
function Tt(e) {
  const t = {
    path: e.path,
    redirect: e.redirect,
    name: e.name,
    meta: e.meta || {},
    aliasOf: e.aliasOf,
    beforeEnter: e.beforeEnter,
    props: Go(e),
    children: e.children || [],
    instances: {},
    leaveGuards: /* @__PURE__ */ new Set(),
    updateGuards: /* @__PURE__ */ new Set(),
    enterCallbacks: {},
    // must be declared afterwards
    // mods: {},
    components: "components" in e ? e.components || null : e.component && { default: e.component }
  };
  return Object.defineProperty(t, "mods", {
    value: {}
  }), t;
}
function Go(e) {
  const t = {}, n = e.props || !1;
  if ("component" in e)
    t.default = n;
  else
    for (const r in e.components)
      t[r] = typeof n == "object" ? n[r] : n;
  return t;
}
function Dt(e) {
  for (; e; ) {
    if (e.record.aliasOf)
      return !0;
    e = e.parent;
  }
  return !1;
}
function Ho(e) {
  return e.reduce((t, n) => V(t, n.meta), {});
}
function jt(e, t) {
  const n = {};
  for (const r in e)
    n[r] = r in t ? t[r] : e[r];
  return n;
}
function ct(e, t) {
  return e.name === t.name && e.optional === t.optional && e.repeatable === t.repeatable;
}
function Ko(e, t) {
  for (const n of e.keys)
    if (!n.optional && !t.keys.find(ct.bind(null, n)))
      return S(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
  for (const n of t.keys)
    if (!n.optional && !e.keys.find(ct.bind(null, n)))
      return S(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
}
function zo(e, t) {
  t && t.record.name && !e.name && !e.path && S(`The route named "${String(t.record.name)}" has a child without a name and an empty path. Using that name won't render the empty path child so you probably want to move the name to the child instead. If this is intentional, add a name to the child route to remove the warning.`);
}
function qo(e, t) {
  for (let n = t; n; n = n.parent)
    if (n.record.name === e.name)
      throw new Error(`A route named "${String(e.name)}" has been added as a ${t === n ? "child" : "descendant"} of a route with the same name. Route names must be unique and a nested route cannot use the same name as an ancestor.`);
}
function Qo(e, t) {
  for (const n of t.keys)
    if (!e.keys.find(ct.bind(null, n)))
      return S(`Absolute path "${e.record.path}" must have the exact same param named "${n.name}" as its parent "${t.record.path}".`);
}
function Jo(e, t) {
  let n = 0, r = t.length;
  for (; n !== r; ) {
    const s = n + r >> 1;
    Pn(e, t[s]) < 0 ? r = s : n = s + 1;
  }
  const o = Yo(e);
  return o && (r = t.lastIndexOf(o, r - 1), P.NODE_ENV !== "production" && r < 0 && S(`Finding ancestor route "${o.record.path}" failed for "${e.record.path}"`)), r;
}
function Yo(e) {
  let t = e;
  for (; t = t.parent; )
    if (Sn(t) && Pn(e, t) === 0)
      return t;
}
function Sn({ record: e }) {
  return !!(e.name || e.components && Object.keys(e.components).length || e.redirect);
}
function Xo(e) {
  const t = {};
  if (e === "" || e === "?")
    return t;
  const r = (e[0] === "?" ? e.slice(1) : e).split("&");
  for (let o = 0; o < r.length; ++o) {
    const s = r[o].replace(pn, " "), i = s.indexOf("="), u = ce(i < 0 ? s : s.slice(0, i)), l = i < 0 ? null : ce(s.slice(i + 1));
    if (u in t) {
      let d = t[u];
      L(d) || (d = t[u] = [d]), d.push(l);
    } else
      t[u] = l;
  }
  return t;
}
function Mt(e) {
  let t = "";
  for (let n in e) {
    const r = e[n];
    if (n = po(n), r == null) {
      r !== void 0 && (t += (t.length ? "&" : "") + n);
      continue;
    }
    (L(r) ? r.map((s) => s && st(s)) : [r && st(r)]).forEach((s) => {
      s !== void 0 && (t += (t.length ? "&" : "") + n, s != null && (t += "=" + s));
    });
  }
  return t;
}
function Zo(e) {
  const t = {};
  for (const n in e) {
    const r = e[n];
    r !== void 0 && (t[n] = L(r) ? r.map((o) => o == null ? null : "" + o) : r == null ? r : "" + r);
  }
  return t;
}
const es = Symbol(P.NODE_ENV !== "production" ? "router view location matched" : ""), Wt = Symbol(P.NODE_ENV !== "production" ? "router view depth" : ""), je = Symbol(P.NODE_ENV !== "production" ? "router" : ""), mt = Symbol(P.NODE_ENV !== "production" ? "route location" : ""), ut = Symbol(P.NODE_ENV !== "production" ? "router view location" : "");
function ge() {
  let e = [];
  function t(r) {
    return e.push(r), () => {
      const o = e.indexOf(r);
      o > -1 && e.splice(o, 1);
    };
  }
  function n() {
    e = [];
  }
  return {
    add: t,
    list: () => e.slice(),
    reset: n
  };
}
function X(e, t, n, r, o, s = (i) => i()) {
  const i = r && // name is defined if record is because of the function overload
  (r.enterCallbacks[o] = r.enterCallbacks[o] || []);
  return () => new Promise((u, l) => {
    const d = (f) => {
      f === !1 ? l(le(4, {
        from: n,
        to: t
      })) : f instanceof Error ? l(f) : Ie(f) ? l(le(2, {
        from: t,
        to: f
      })) : (i && // since enterCallbackArray is truthy, both record and name also are
      r.enterCallbacks[o] === i && typeof f == "function" && i.push(f), u());
    }, a = s(() => e.call(r && r.instances[o], t, n, P.NODE_ENV !== "production" ? ts(d, t, n) : d));
    let c = Promise.resolve(a);
    if (e.length < 3 && (c = c.then(d)), P.NODE_ENV !== "production" && e.length > 2) {
      const f = `The "next" callback was never called inside of ${e.name ? '"' + e.name + '"' : ""}:
${e.toString()}
. If you are returning a value instead of calling "next", make sure to remove the "next" parameter from your function.`;
      if (typeof a == "object" && "then" in a)
        c = c.then((h) => d._called ? h : (S(f), Promise.reject(new Error("Invalid navigation guard"))));
      else if (a !== void 0 && !d._called) {
        S(f), l(new Error("Invalid navigation guard"));
        return;
      }
    }
    c.catch((f) => l(f));
  });
}
function ts(e, t, n) {
  let r = 0;
  return function() {
    r++ === 1 && S(`The "next" callback was called more than once in one navigation guard when going from "${n.fullPath}" to "${t.fullPath}". It should be called exactly one time in each navigation guard. This will fail in production.`), e._called = !0, r === 1 && e.apply(null, arguments);
  };
}
function qe(e, t, n, r, o = (s) => s()) {
  const s = [];
  for (const i of e) {
    P.NODE_ENV !== "production" && !i.components && !i.children.length && S(`Record with path "${i.path}" is either missing a "component(s)" or "children" property.`);
    for (const u in i.components) {
      let l = i.components[u];
      if (P.NODE_ENV !== "production") {
        if (!l || typeof l != "object" && typeof l != "function")
          throw S(`Component "${u}" in record with path "${i.path}" is not a valid component. Received "${String(l)}".`), new Error("Invalid route component");
        if ("then" in l) {
          S(`Component "${u}" in record with path "${i.path}" is a Promise instead of a function that returns a Promise. Did you write "import('./MyPage.vue')" instead of "() => import('./MyPage.vue')" ? This will break in production if not fixed.`);
          const d = l;
          l = () => d;
        } else l.__asyncLoader && // warn only once per component
        !l.__warnedDefineAsync && (l.__warnedDefineAsync = !0, S(`Component "${u}" in record with path "${i.path}" is defined using "defineAsyncComponent()". Write "() => import('./MyPage.vue')" instead of "defineAsyncComponent(() => import('./MyPage.vue'))".`));
      }
      if (!(t !== "beforeRouteEnter" && !i.instances[u]))
        if (dn(l)) {
          const a = (l.__vccOpts || l)[t];
          a && s.push(X(a, n, r, i, u, o));
        } else {
          let d = l();
          P.NODE_ENV !== "production" && !("catch" in d) && (S(`Component "${u}" in record with path "${i.path}" is a function that does not return a Promise. If you were passing a functional component, make sure to add a "displayName" to the component. This will break in production if not fixed.`), d = Promise.resolve(d)), s.push(() => d.then((a) => {
            if (!a)
              throw new Error(`Couldn't resolve component "${u}" at "${i.path}"`);
            const c = no(a) ? a.default : a;
            i.mods[u] = a, i.components[u] = c;
            const h = (c.__vccOpts || c)[t];
            return h && X(h, n, r, i, u, o)();
          }));
        }
    }
  }
  return s;
}
function Bt(e) {
  const t = z(je), n = z(mt);
  let r = !1, o = null;
  const s = W(() => {
    const a = M(e.to);
    return P.NODE_ENV !== "production" && (!r || a !== o) && (Ie(a) || (r ? S(`Invalid value for prop "to" in useLink()
- to:`, a, `
- previous to:`, o, `
- props:`, e) : S(`Invalid value for prop "to" in useLink()
- to:`, a, `
- props:`, e)), o = a, r = !0), t.resolve(a);
  }), i = W(() => {
    const { matched: a } = s.value, { length: c } = a, f = a[c - 1], h = n.matched;
    if (!f || !h.length)
      return -1;
    const g = h.findIndex(Z.bind(null, f));
    if (g > -1)
      return g;
    const m = Lt(a[c - 2]);
    return (
      // we are dealing with nested routes
      c > 1 && // if the parent and matched route have the same path, this link is
      // referring to the empty child. Or we currently are on a different
      // child of the same parent
      Lt(f) === m && // avoid comparing the child with its parent
      h[h.length - 1].path !== m ? h.findIndex(Z.bind(null, a[c - 2])) : g
    );
  }), u = W(() => i.value > -1 && is(n.params, s.value.params)), l = W(() => i.value > -1 && i.value === n.matched.length - 1 && yn(n.params, s.value.params));
  function d(a = {}) {
    if (ss(a)) {
      const c = t[M(e.replace) ? "replace" : "push"](
        M(e.to)
        // avoid uncaught errors are they are logged anyway
      ).catch(Ee);
      return e.viewTransition && typeof document < "u" && "startViewTransition" in document && document.startViewTransition(() => c), c;
    }
    return Promise.resolve();
  }
  if (P.NODE_ENV !== "production" && Q) {
    const a = Qt();
    if (a) {
      const c = {
        route: s.value,
        isActive: u.value,
        isExactActive: l.value,
        error: null
      };
      a.__vrl_devtools = a.__vrl_devtools || [], a.__vrl_devtools.push(c), zt(() => {
        c.route = s.value, c.isActive = u.value, c.isExactActive = l.value, c.error = Ie(M(e.to)) ? null : 'Invalid "to" value';
      }, { flush: "post" });
    }
  }
  return {
    route: s,
    href: W(() => s.value.href),
    isActive: u,
    isExactActive: l,
    navigate: d
  };
}
function ns(e) {
  return e.length === 1 ? e[0] : e;
}
const rs = /* @__PURE__ */ D({
  name: "RouterLink",
  compatConfig: { MODE: 3 },
  props: {
    to: {
      type: [String, Object],
      required: !0
    },
    replace: Boolean,
    activeClass: String,
    // inactiveClass: String,
    exactActiveClass: String,
    custom: Boolean,
    ariaCurrentValue: {
      type: String,
      default: "page"
    }
  },
  useLink: Bt,
  setup(e, { slots: t }) {
    const n = qn(Bt(e)), { options: r } = z(je), o = W(() => ({
      [Ft(e.activeClass, r.linkActiveClass, "router-link-active")]: n.isActive,
      // [getLinkClass(
      //   props.inactiveClass,
      //   options.linkInactiveClass,
      //   'router-link-inactive'
      // )]: !link.isExactActive,
      [Ft(e.exactActiveClass, r.linkExactActiveClass, "router-link-exact-active")]: n.isExactActive
    }));
    return () => {
      const s = t.default && ns(t.default(n));
      return e.custom ? s : x("a", {
        "aria-current": n.isExactActive ? e.ariaCurrentValue : null,
        href: n.href,
        // this would override user added attrs but Vue will still add
        // the listener, so we end up triggering both
        onClick: n.navigate,
        class: o.value
      }, s);
    };
  }
}), os = rs;
function ss(e) {
  if (!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey) && !e.defaultPrevented && !(e.button !== void 0 && e.button !== 0)) {
    if (e.currentTarget && e.currentTarget.getAttribute) {
      const t = e.currentTarget.getAttribute("target");
      if (/\b_blank\b/i.test(t))
        return;
    }
    return e.preventDefault && e.preventDefault(), !0;
  }
}
function is(e, t) {
  for (const n in t) {
    const r = t[n], o = e[n];
    if (typeof r == "string") {
      if (r !== o)
        return !1;
    } else if (!L(o) || o.length !== r.length || r.some((s, i) => s !== o[i]))
      return !1;
  }
  return !0;
}
function Lt(e) {
  return e ? e.aliasOf ? e.aliasOf.path : e.path : "";
}
const Ft = (e, t, n) => e ?? t ?? n, as = /* @__PURE__ */ D({
  name: "RouterView",
  // #674 we manually inherit them
  inheritAttrs: !1,
  props: {
    name: {
      type: String,
      default: "default"
    },
    route: Object
  },
  // Better compat for @vue/compat users
  // https://github.com/vuejs/router/issues/1315
  compatConfig: { MODE: 3 },
  setup(e, { attrs: t, slots: n }) {
    P.NODE_ENV !== "production" && us();
    const r = z(ut), o = W(() => e.route || r.value), s = z(Wt, 0), i = W(() => {
      let d = M(s);
      const { matched: a } = o.value;
      let c;
      for (; (c = a[d]) && !c.components; )
        d++;
      return d;
    }), u = W(() => o.value.matched[i.value]);
    ae(Wt, W(() => i.value + 1)), ae(es, u), ae(ut, o);
    const l = J();
    return K(() => [l.value, u.value, e.name], ([d, a, c], [f, h, g]) => {
      a && (a.instances[c] = d, h && h !== a && d && d === f && (a.leaveGuards.size || (a.leaveGuards = h.leaveGuards), a.updateGuards.size || (a.updateGuards = h.updateGuards))), d && a && // if there is no instance but to and from are the same this might be
      // the first visit
      (!h || !Z(a, h) || !f) && (a.enterCallbacks[c] || []).forEach((m) => m(d));
    }, { flush: "post" }), () => {
      const d = o.value, a = e.name, c = u.value, f = c && c.components[a];
      if (!f)
        return Ut(n.default, { Component: f, route: d });
      const h = c.props[a], g = h ? h === !0 ? d.params : typeof h == "function" ? h(d) : h : null, v = x(f, V({}, g, t, {
        onVnodeUnmounted: (_) => {
          _.component.isUnmounted && (c.instances[a] = null);
        },
        ref: l
      }));
      if (P.NODE_ENV !== "production" && Q && v.ref) {
        const _ = {
          depth: i.value,
          name: c.name,
          path: c.path,
          meta: c.meta
        };
        (L(v.ref) ? v.ref.map((R) => R.i) : [v.ref.i]).forEach((R) => {
          R.__vrv_devtools = _;
        });
      }
      return (
        // pass the vnode to the slot as a prop.
        // h and <component :is="..."> both accept vnodes
        Ut(n.default, { Component: v, route: d }) || v
      );
    };
  }
});
function Ut(e, t) {
  if (!e)
    return null;
  const n = e(t);
  return n.length === 1 ? n[0] : n;
}
const cs = as;
function us() {
  const e = Qt(), t = e.parent && e.parent.type.name, n = e.parent && e.parent.subTree && e.parent.subTree.type;
  if (t && (t === "KeepAlive" || t.includes("Transition")) && typeof n == "object" && n.name === "RouterView") {
    const r = t === "KeepAlive" ? "keep-alive" : "transition";
    S(`<router-view> can no longer be used directly inside <transition> or <keep-alive>.
Use slot props instead:

<router-view v-slot="{ Component }">
  <${r}>
    <component :is="Component" />
  </${r}>
</router-view>`);
  }
}
function me(e, t) {
  const n = V({}, e, {
    // remove variables that can contain vue instances
    matched: e.matched.map((r) => _s(r, ["instances", "children", "aliasOf"]))
  });
  return {
    _custom: {
      type: null,
      readOnly: !0,
      display: e.fullPath,
      tooltip: t,
      value: n
    }
  };
}
function Oe(e) {
  return {
    _custom: {
      display: e
    }
  };
}
let ls = 0;
function fs(e, t, n) {
  if (t.__hasDevtools)
    return;
  t.__hasDevtools = !0;
  const r = ls++;
  to({
    id: "org.vuejs.router" + (r ? "." + r : ""),
    label: "Vue Router",
    packageName: "vue-router",
    homepage: "https://router.vuejs.org",
    logo: "https://router.vuejs.org/logo.png",
    componentStateTypes: ["Routing"],
    app: e
  }, (o) => {
    typeof o.now != "function" && console.warn("[Vue Router]: You seem to be using an outdated version of Vue Devtools. Are you still using the Beta release instead of the stable one? You can find the links at https://devtools.vuejs.org/guide/installation.html."), o.on.inspectComponent((a, c) => {
      a.instanceData && a.instanceData.state.push({
        type: "Routing",
        key: "$route",
        editable: !1,
        value: me(t.currentRoute.value, "Current Route")
      });
    }), o.on.visitComponentTree(({ treeNode: a, componentInstance: c }) => {
      if (c.__vrv_devtools) {
        const f = c.__vrv_devtools;
        a.tags.push({
          label: (f.name ? `${f.name.toString()}: ` : "") + f.path,
          textColor: 0,
          tooltip: "This component is rendered by &lt;router-view&gt;",
          backgroundColor: On
        });
      }
      L(c.__vrl_devtools) && (c.__devtoolsApi = o, c.__vrl_devtools.forEach((f) => {
        let h = f.route.path, g = Vn, m = "", v = 0;
        f.error ? (h = f.error, g = ms, v = vs) : f.isExactActive ? (g = Nn, m = "This is exactly active") : f.isActive && (g = kn, m = "This link is active"), a.tags.push({
          label: h,
          textColor: v,
          tooltip: m,
          backgroundColor: g
        });
      }));
    }), K(t.currentRoute, () => {
      l(), o.notifyComponentUpdate(), o.sendInspectorTree(u), o.sendInspectorState(u);
    });
    const s = "router:navigations:" + r;
    o.addTimelineLayer({
      id: s,
      label: `Router${r ? " " + r : ""} Navigations`,
      color: 4237508
    }), t.onError((a, c) => {
      o.addTimelineEvent({
        layerId: s,
        event: {
          title: "Error during Navigation",
          subtitle: c.fullPath,
          logType: "error",
          time: o.now(),
          data: { error: a },
          groupId: c.meta.__navigationId
        }
      });
    });
    let i = 0;
    t.beforeEach((a, c) => {
      const f = {
        guard: Oe("beforeEach"),
        from: me(c, "Current Location during this navigation"),
        to: me(a, "Target location")
      };
      Object.defineProperty(a.meta, "__navigationId", {
        value: i++
      }), o.addTimelineEvent({
        layerId: s,
        event: {
          time: o.now(),
          title: "Start of navigation",
          subtitle: a.fullPath,
          data: f,
          groupId: a.meta.__navigationId
        }
      });
    }), t.afterEach((a, c, f) => {
      const h = {
        guard: Oe("afterEach")
      };
      f ? (h.failure = {
        _custom: {
          type: Error,
          readOnly: !0,
          display: f ? f.message : "",
          tooltip: "Navigation Failure",
          value: f
        }
      }, h.status = Oe("❌")) : h.status = Oe("✅"), h.from = me(c, "Current Location during this navigation"), h.to = me(a, "Target location"), o.addTimelineEvent({
        layerId: s,
        event: {
          title: "End of navigation",
          subtitle: a.fullPath,
          time: o.now(),
          data: h,
          logType: f ? "warning" : "default",
          groupId: a.meta.__navigationId
        }
      });
    });
    const u = "router-inspector:" + r;
    o.addInspector({
      id: u,
      label: "Routes" + (r ? " " + r : ""),
      icon: "book",
      treeFilterPlaceholder: "Search routes"
    });
    function l() {
      if (!d)
        return;
      const a = d;
      let c = n.getRoutes().filter((f) => !f.parent || // these routes have a parent with no component which will not appear in the view
      // therefore we still need to include them
      !f.parent.record.components);
      c.forEach(An), a.filter && (c = c.filter((f) => (
        // save matches state based on the payload
        lt(f, a.filter.toLowerCase())
      ))), c.forEach((f) => In(f, t.currentRoute.value)), a.rootNodes = c.map(Cn);
    }
    let d;
    o.on.getInspectorTree((a) => {
      d = a, a.app === e && a.inspectorId === u && l();
    }), o.on.getInspectorState((a) => {
      if (a.app === e && a.inspectorId === u) {
        const f = n.getRoutes().find((h) => h.record.__vd_id === a.nodeId);
        f && (a.state = {
          options: hs(f)
        });
      }
    }), o.sendInspectorTree(u), o.sendInspectorState(u);
  });
}
function ds(e) {
  return e.optional ? e.repeatable ? "*" : "?" : e.repeatable ? "+" : "";
}
function hs(e) {
  const { record: t } = e, n = [
    { editable: !1, key: "path", value: t.path }
  ];
  return t.name != null && n.push({
    editable: !1,
    key: "name",
    value: t.name
  }), n.push({ editable: !1, key: "regexp", value: e.re }), e.keys.length && n.push({
    editable: !1,
    key: "keys",
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.keys.map((r) => `${r.name}${ds(r)}`).join(" "),
        tooltip: "Param keys",
        value: e.keys
      }
    }
  }), t.redirect != null && n.push({
    editable: !1,
    key: "redirect",
    value: t.redirect
  }), e.alias.length && n.push({
    editable: !1,
    key: "aliases",
    value: e.alias.map((r) => r.record.path)
  }), Object.keys(e.record.meta).length && n.push({
    editable: !1,
    key: "meta",
    value: e.record.meta
  }), n.push({
    key: "score",
    editable: !1,
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.score.map((r) => r.join(", ")).join(" | "),
        tooltip: "Score used to sort routes",
        value: e.score
      }
    }
  }), n;
}
const On = 15485081, kn = 2450411, Nn = 8702998, ps = 2282478, Vn = 16486972, gs = 6710886, ms = 16704226, vs = 12131356;
function Cn(e) {
  const t = [], { record: n } = e;
  n.name != null && t.push({
    label: String(n.name),
    textColor: 0,
    backgroundColor: ps
  }), n.aliasOf && t.push({
    label: "alias",
    textColor: 0,
    backgroundColor: Vn
  }), e.__vd_match && t.push({
    label: "matches",
    textColor: 0,
    backgroundColor: On
  }), e.__vd_exactActive && t.push({
    label: "exact",
    textColor: 0,
    backgroundColor: Nn
  }), e.__vd_active && t.push({
    label: "active",
    textColor: 0,
    backgroundColor: kn
  }), n.redirect && t.push({
    label: typeof n.redirect == "string" ? `redirect: ${n.redirect}` : "redirects",
    textColor: 16777215,
    backgroundColor: gs
  });
  let r = n.__vd_id;
  return r == null && (r = String(ys++), n.__vd_id = r), {
    id: r,
    label: n.path,
    tags: t,
    children: e.children.map(Cn)
  };
}
let ys = 0;
const Es = /^\/(.*)\/([a-z]*)$/;
function In(e, t) {
  const n = t.matched.length && Z(t.matched[t.matched.length - 1], e.record);
  e.__vd_exactActive = e.__vd_active = n, n || (e.__vd_active = t.matched.some((r) => Z(r, e.record))), e.children.forEach((r) => In(r, t));
}
function An(e) {
  e.__vd_match = !1, e.children.forEach(An);
}
function lt(e, t) {
  const n = String(e.re).match(Es);
  if (e.__vd_match = !1, !n || n.length < 3)
    return !1;
  if (new RegExp(n[1].replace(/\$$/, ""), n[2]).test(t))
    return e.children.forEach((i) => lt(i, t)), e.record.path !== "/" || t === "/" ? (e.__vd_match = e.re.test(t), !0) : !1;
  const o = e.record.path.toLowerCase(), s = ce(o);
  return !t.startsWith("/") && (s.includes(t) || o.includes(t)) || s.startsWith(t) || o.startsWith(t) || e.record.name && String(e.record.name).includes(t) ? !0 : e.children.some((i) => lt(i, t));
}
function _s(e, t) {
  const n = {};
  for (const r in e)
    t.includes(r) || (n[r] = e[r]);
  return n;
}
function ws(e) {
  const t = Uo(e.routes, e), n = e.parseQuery || Xo, r = e.stringifyQuery || Mt, o = e.history;
  if (P.NODE_ENV !== "production" && !o)
    throw new Error('Provide the "history" option when calling "createRouter()": https://router.vuejs.org/api/interfaces/RouterOptions.html#history');
  const s = ge(), i = ge(), u = ge(), l = G(Y);
  let d = Y;
  Q && e.scrollBehavior && "scrollRestoration" in history && (history.scrollRestoration = "manual");
  const a = He.bind(null, (p) => "" + p), c = He.bind(null, mo), f = (
    // @ts-expect-error: intentionally avoid the type check
    He.bind(null, ce)
  );
  function h(p, E) {
    let y, w;
    return Rn(p) ? (y = t.getRecordMatcher(p), P.NODE_ENV !== "production" && !y && S(`Parent route "${String(p)}" not found when adding child route`, E), w = E) : w = p, t.addRoute(w, y);
  }
  function g(p) {
    const E = t.getRecordMatcher(p);
    E ? t.removeRoute(E) : P.NODE_ENV !== "production" && S(`Cannot remove non-existent route "${String(p)}"`);
  }
  function m() {
    return t.getRoutes().map((p) => p.record);
  }
  function v(p) {
    return !!t.getRecordMatcher(p);
  }
  function _(p, E) {
    if (E = V({}, E || l.value), typeof p == "string") {
      const O = Ke(n, p, E.path), I = t.resolve({ path: O.path }, E), ee = o.createHref(O.fullPath);
      return P.NODE_ENV !== "production" && (ee.startsWith("//") ? S(`Location "${p}" resolved to "${ee}". A resolved location cannot start with multiple slashes.`) : I.matched.length || S(`No match found for location with path "${p}"`)), V(O, I, {
        params: f(I.params),
        hash: ce(O.hash),
        redirectedFrom: void 0,
        href: ee
      });
    }
    if (P.NODE_ENV !== "production" && !Ie(p))
      return S(`router.resolve() was passed an invalid location. This will fail in production.
- Location:`, p), _({});
    let y;
    if (p.path != null)
      P.NODE_ENV !== "production" && "params" in p && !("name" in p) && // @ts-expect-error: the type is never
      Object.keys(p.params).length && S(`Path "${p.path}" was passed with params but they will be ignored. Use a named route alongside params instead.`), y = V({}, p, {
        path: Ke(n, p.path, E.path).path
      });
    else {
      const O = V({}, p.params);
      for (const I in O)
        O[I] == null && delete O[I];
      y = V({}, p, {
        params: c(O)
      }), E.params = c(E.params);
    }
    const w = t.resolve(y, E), C = p.hash || "";
    P.NODE_ENV !== "production" && C && !C.startsWith("#") && S(`A \`hash\` should always start with the character "#". Replace "${C}" with "#${C}".`), w.params = a(f(w.params));
    const A = Eo(r, V({}, p, {
      hash: ho(C),
      path: w.path
    })), k = o.createHref(A);
    return P.NODE_ENV !== "production" && (k.startsWith("//") ? S(`Location "${p}" resolved to "${k}". A resolved location cannot start with multiple slashes.`) : w.matched.length || S(`No match found for location with path "${p.path != null ? p.path : p}"`)), V({
      fullPath: A,
      // keep the hash encoded so fullPath is effectively path + encodedQuery +
      // hash
      hash: C,
      query: (
        // if the user is using a custom query lib like qs, we might have
        // nested objects, so we keep the query as is, meaning it can contain
        // numbers at `$route.query`, but at the point, the user will have to
        // use their own type anyway.
        // https://github.com/vuejs/router/issues/328#issuecomment-649481567
        r === Mt ? Zo(p.query) : p.query || {}
      )
    }, w, {
      redirectedFrom: void 0,
      href: k
    });
  }
  function b(p) {
    return typeof p == "string" ? Ke(n, p, l.value.path) : V({}, p);
  }
  function R(p, E) {
    if (d !== p)
      return le(8, {
        from: E,
        to: p
      });
  }
  function N(p) {
    return F(p);
  }
  function j(p) {
    return N(V(b(p), { replace: !0 }));
  }
  function U(p) {
    const E = p.matched[p.matched.length - 1];
    if (E && E.redirect) {
      const { redirect: y } = E;
      let w = typeof y == "function" ? y(p) : y;
      if (typeof w == "string" && (w = w.includes("?") || w.includes("#") ? w = b(w) : (
        // force empty params
        { path: w }
      ), w.params = {}), P.NODE_ENV !== "production" && w.path == null && !("name" in w))
        throw S(`Invalid redirect found:
${JSON.stringify(w, null, 2)}
 when navigating to "${p.fullPath}". A redirect must contain a name or path. This will break in production.`), new Error("Invalid redirect");
      return V({
        query: p.query,
        hash: p.hash,
        // avoid transferring params if the redirect has a path
        params: w.path != null ? {} : p.params
      }, w);
    }
  }
  function F(p, E) {
    const y = d = _(p), w = l.value, C = p.state, A = p.force, k = p.replace === !0, O = U(y);
    if (O)
      return F(
        V(b(O), {
          state: typeof O == "object" ? V({}, C, O.state) : C,
          force: A,
          replace: k
        }),
        // keep original redirectedFrom if it exists
        E || y
      );
    const I = y;
    I.redirectedFrom = E;
    let ee;
    return !A && kt(r, w, y) && (ee = le(16, { to: I, from: w }), wt(
      w,
      w,
      // this is a push, the only way for it to be triggered from a
      // history.listen is with a redirect, which makes it become a push
      !0,
      // This cannot be the first navigation because the initial location
      // cannot be manually navigated to
      !1
    )), (ee ? Promise.resolve(ee) : vt(I, w)).catch((T) => q(T) ? (
      // navigation redirects still mark the router as ready
      q(
        T,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? T : Le(T)
    ) : (
      // reject any unknown error
      Be(T, I, w)
    )).then((T) => {
      if (T) {
        if (q(
          T,
          2
          /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
        ))
          return P.NODE_ENV !== "production" && // we are redirecting to the same location we were already at
          kt(r, _(T.to), I) && // and we have done it a couple of times
          E && // @ts-expect-error: added only in dev
          (E._count = E._count ? (
            // @ts-expect-error
            E._count + 1
          ) : 1) > 30 ? (S(`Detected a possibly infinite redirection in a navigation guard when going from "${w.fullPath}" to "${I.fullPath}". Aborting to avoid a Stack Overflow.
 Are you always returning a new location within a navigation guard? That would lead to this error. Only return when redirecting or aborting, that should fix this. This might break in production if not fixed.`), Promise.reject(new Error("Infinite redirect in navigation guard"))) : F(
            // keep options
            V({
              // preserve an existing replacement but allow the redirect to override it
              replace: k
            }, b(T.to), {
              state: typeof T.to == "object" ? V({}, C, T.to.state) : C,
              force: A
            }),
            // preserve the original redirectedFrom if any
            E || I
          );
      } else
        T = Et(I, w, !0, k, C);
      return yt(I, w, T), T;
    });
  }
  function Bn(p, E) {
    const y = R(p, E);
    return y ? Promise.reject(y) : Promise.resolve();
  }
  function Me(p) {
    const E = Se.values().next().value;
    return E && typeof E.runWithContext == "function" ? E.runWithContext(p) : p();
  }
  function vt(p, E) {
    let y;
    const [w, C, A] = bs(p, E);
    y = qe(w.reverse(), "beforeRouteLeave", p, E);
    for (const O of w)
      O.leaveGuards.forEach((I) => {
        y.push(X(I, p, E));
      });
    const k = Bn.bind(null, p, E);
    return y.push(k), re(y).then(() => {
      y = [];
      for (const O of s.list())
        y.push(X(O, p, E));
      return y.push(k), re(y);
    }).then(() => {
      y = qe(C, "beforeRouteUpdate", p, E);
      for (const O of C)
        O.updateGuards.forEach((I) => {
          y.push(X(I, p, E));
        });
      return y.push(k), re(y);
    }).then(() => {
      y = [];
      for (const O of A)
        if (O.beforeEnter)
          if (L(O.beforeEnter))
            for (const I of O.beforeEnter)
              y.push(X(I, p, E));
          else
            y.push(X(O.beforeEnter, p, E));
      return y.push(k), re(y);
    }).then(() => (p.matched.forEach((O) => O.enterCallbacks = {}), y = qe(A, "beforeRouteEnter", p, E, Me), y.push(k), re(y))).then(() => {
      y = [];
      for (const O of i.list())
        y.push(X(O, p, E));
      return y.push(k), re(y);
    }).catch((O) => q(
      O,
      8
      /* ErrorTypes.NAVIGATION_CANCELLED */
    ) ? O : Promise.reject(O));
  }
  function yt(p, E, y) {
    u.list().forEach((w) => Me(() => w(p, E, y)));
  }
  function Et(p, E, y, w, C) {
    const A = R(p, E);
    if (A)
      return A;
    const k = E === Y, O = Q ? history.state : {};
    y && (w || k ? o.replace(p.fullPath, V({
      scroll: k && O && O.scroll
    }, C)) : o.push(p.fullPath, C)), l.value = p, wt(p, E, y, k), Le();
  }
  let he;
  function Ln() {
    he || (he = o.listen((p, E, y) => {
      if (!bt.listening)
        return;
      const w = _(p), C = U(w);
      if (C) {
        F(V(C, { replace: !0, force: !0 }), w).catch(Ee);
        return;
      }
      d = w;
      const A = l.value;
      Q && So(Vt(A.fullPath, y.delta), De()), vt(w, A).catch((k) => q(
        k,
        12
        /* ErrorTypes.NAVIGATION_CANCELLED */
      ) ? k : q(
        k,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? (F(
        V(b(k.to), {
          force: !0
        }),
        w
        // avoid an uncaught rejection, let push call triggerError
      ).then((O) => {
        q(
          O,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && !y.delta && y.type === ue.pop && o.go(-1, !1);
      }).catch(Ee), Promise.reject()) : (y.delta && o.go(-y.delta, !1), Be(k, w, A))).then((k) => {
        k = k || Et(
          // after navigation, all matched components are resolved
          w,
          A,
          !1
        ), k && (y.delta && // a new navigation has been triggered, so we do not want to revert, that will change the current history
        // entry while a different route is displayed
        !q(
          k,
          8
          /* ErrorTypes.NAVIGATION_CANCELLED */
        ) ? o.go(-y.delta, !1) : y.type === ue.pop && q(
          k,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && o.go(-1, !1)), yt(w, A, k);
      }).catch(Ee);
    }));
  }
  let We = ge(), _t = ge(), Pe;
  function Be(p, E, y) {
    Le(p);
    const w = _t.list();
    return w.length ? w.forEach((C) => C(p, E, y)) : (P.NODE_ENV !== "production" && S("uncaught error during route navigation:"), console.error(p)), Promise.reject(p);
  }
  function Fn() {
    return Pe && l.value !== Y ? Promise.resolve() : new Promise((p, E) => {
      We.add([p, E]);
    });
  }
  function Le(p) {
    return Pe || (Pe = !p, Ln(), We.list().forEach(([E, y]) => p ? y(p) : E()), We.reset()), p;
  }
  function wt(p, E, y, w) {
    const { scrollBehavior: C } = e;
    if (!Q || !C)
      return Promise.resolve();
    const A = !y && Oo(Vt(p.fullPath, 0)) || (w || !y) && history.state && history.state.scroll || null;
    return ke().then(() => C(p, E, A)).then((k) => k && Po(k)).catch((k) => Be(k, p, E));
  }
  const Fe = (p) => o.go(p);
  let Ue;
  const Se = /* @__PURE__ */ new Set(), bt = {
    currentRoute: l,
    listening: !0,
    addRoute: h,
    removeRoute: g,
    clearRoutes: t.clearRoutes,
    hasRoute: v,
    getRoutes: m,
    resolve: _,
    options: e,
    push: N,
    replace: j,
    go: Fe,
    back: () => Fe(-1),
    forward: () => Fe(1),
    beforeEach: s.add,
    beforeResolve: i.add,
    afterEach: u.add,
    onError: _t.add,
    isReady: Fn,
    install(p) {
      const E = this;
      p.component("RouterLink", os), p.component("RouterView", cs), p.config.globalProperties.$router = E, Object.defineProperty(p.config.globalProperties, "$route", {
        enumerable: !0,
        get: () => M(l)
      }), Q && // used for the initial navigation client side to avoid pushing
      // multiple times when the router is used in multiple apps
      !Ue && l.value === Y && (Ue = !0, N(o.location).catch((C) => {
        P.NODE_ENV !== "production" && S("Unexpected error when starting the router:", C);
      }));
      const y = {};
      for (const C in Y)
        Object.defineProperty(y, C, {
          get: () => l.value[C],
          enumerable: !0
        });
      p.provide(je, E), p.provide(mt, zn(y)), p.provide(ut, l);
      const w = p.unmount;
      Se.add(p), p.unmount = function() {
        Se.delete(p), Se.size < 1 && (d = Y, he && he(), he = null, l.value = Y, Ue = !1, Pe = !1), w();
      }, P.NODE_ENV !== "production" && Q && fs(p, E, t);
    }
  };
  function re(p) {
    return p.reduce((E, y) => E.then(() => Me(y)), Promise.resolve());
  }
  return bt;
}
function bs(e, t) {
  const n = [], r = [], o = [], s = Math.max(t.matched.length, e.matched.length);
  for (let i = 0; i < s; i++) {
    const u = t.matched[i];
    u && (e.matched.find((d) => Z(d, u)) ? r.push(u) : n.push(u));
    const l = e.matched[i];
    l && (t.matched.find((d) => Z(d, l)) || o.push(l));
  }
  return [n, r, o];
}
function Rs() {
  return z(je);
}
function Ps(e) {
  return z(mt);
}
function Ss(e) {
  const { immediately: t = !1, code: n } = e;
  let r = B(n);
  return t && (r = r()), r;
}
const _e = /* @__PURE__ */ new Map();
function Os(e) {
  if (!_e.has(e)) {
    const t = Symbol();
    return _e.set(e, t), t;
  }
  return _e.get(e);
}
function de(e, t) {
  var u, l;
  const n = Ge(e), r = Ns(n, t);
  if (r.size > 0) {
    const d = Os(e);
    ae(d, r);
  }
  const o = ne({ attached: { varMap: r, sid: e } });
  xr({
    watchConfigs: n.py_watch || [],
    computedConfigs: n.web_computed || [],
    varMapGetter: o,
    sid: e
  }), (u = n.js_watch) == null || u.forEach((d) => {
    Hr(d, o);
  }), (l = n.vue_watch) == null || l.forEach((d) => {
    Gr(d, o);
  });
  function s(d, a) {
    const c = Ge(d);
    if (!c.vfor)
      return;
    const { fi: f } = c.vfor;
    f && (r.get(f.id).value = a.index);
  }
  function i(d) {
    const { sid: a, value: c } = d;
    if (!a)
      return;
    const f = Ge(a), { id: h } = f.sp, g = r.get(h);
    g.value = c;
  }
  return {
    updateVforInfo: s,
    updateSlotPropValue: i
  };
}
function ne(e) {
  const { attached: t, sidCollector: n } = e || {}, [r, o, s] = Vs(n);
  t && r.set(t.sid, t.varMap);
  const i = o ? Ps() : null, u = s ? Rs() : null, l = o ? () => i : () => {
    throw new Error("Route params not found");
  }, d = s ? () => u : () => {
    throw new Error("Router not found");
  };
  function a(m) {
    const v = Je(f(m));
    return nn(v, m.path ?? [], a);
  }
  function c(m) {
    const v = f(m);
    return Er(v, {
      paths: m.path,
      getBindableValueFn: a
    });
  }
  function f(m) {
    return kr(m) ? () => l()[m.prop] : r.get(m.sid).get(m.id);
  }
  function h(m, v) {
    if (pt(m)) {
      const _ = f(m);
      if (m.path) {
        rn(_.value, m.path, v, a);
        return;
      }
      _.value = v;
      return;
    }
    throw new Error(`Unsupported output binding: ${m}`);
  }
  function g() {
    return d();
  }
  return {
    getValue: a,
    getRouter: g,
    getVueRefObject: c,
    updateValue: h,
    getVueRefObjectWithoutPath: f
  };
}
function $n(e) {
  const t = _e.get(e);
  return z(t);
}
function ks(e) {
  const t = $n(e);
  if (t === void 0)
    throw new Error(`Scope not found: ${e}`);
  return t;
}
function Ns(e, t) {
  var o, s, i, u, l, d;
  const n = /* @__PURE__ */ new Map(), r = ne({
    attached: { varMap: n, sid: e.id }
  });
  if (e.data && e.data.forEach((a) => {
    n.set(a.id, a.value);
  }), e.jsFn && e.jsFn.forEach((a) => {
    const c = Ss(a);
    n.set(a.id, () => c);
  }), e.vfor && (t != null && t.initVforInfo)) {
    const { fv: a, fi: c, fk: f } = e.vfor, { index: h = 0, keyValue: g = null, config: m } = t.initVforInfo, { sid: v } = m, _ = zr(v);
    if (a) {
      const b = ie(() => ({
        get() {
          const R = _.value;
          return Array.isArray(R) ? R[h] : Object.values(R)[h];
        },
        set(R) {
          const N = _.value;
          if (!Array.isArray(N)) {
            N[g] = R;
            return;
          }
          N[h] = R;
        }
      }));
      n.set(a.id, b);
    }
    c && n.set(c.id, G(h)), f && n.set(f.id, G(g));
  }
  if (e.sp) {
    const { id: a } = e.sp, c = ((o = t == null ? void 0 : t.initSlotPropInfo) == null ? void 0 : o.value) || null;
    n.set(a, G(c));
  }
  return (s = e.eRefs) == null || s.forEach((a) => {
    n.set(a.id, G(null));
  }), (i = e.refs) == null || i.forEach((a) => {
    const c = _r(a);
    n.set(a.id, c);
  }), (u = e.web_computed) == null || u.forEach((a) => {
    const c = br(a);
    n.set(a.id, c);
  }), (l = e.js_computed) == null || l.forEach((a) => {
    const c = Rr(
      a,
      r
    );
    n.set(a.id, c);
  }), (d = e.vue_computed) == null || d.forEach((a) => {
    const c = wr(
      a,
      r
    );
    n.set(a.id, c);
  }), n;
}
function Vs(e) {
  const t = /* @__PURE__ */ new Map();
  if (e) {
    const { sids: n, needRouteParams: r = !0, needRouter: o = !0 } = e;
    for (const s of n)
      t.set(s, ks(s));
    return [t, r, o];
  }
  for (const n of _e.keys()) {
    const r = $n(n);
    r !== void 0 && t.set(n, r);
  }
  return [t, !0, !0];
}
const Cs = D(Is, {
  props: ["vforConfig", "vforIndex", "vforKeyValue"]
});
function Is(e) {
  const { sid: t, items: n = [] } = e.vforConfig, { updateVforInfo: r } = de(t, {
    initVforInfo: {
      config: e.vforConfig,
      index: e.vforIndex,
      keyValue: e.vforKeyValue
    }
  });
  return () => (r(t, {
    index: e.vforIndex,
    keyValue: e.vforKeyValue
  }), n.length === 1 ? fe(n[0]) : n.map((o) => fe(o)));
}
function Gt(e) {
  const { start: t = 0, end: n, step: r = 1 } = e;
  let o = [];
  if (r > 0)
    for (let s = t; s < n; s += r)
      o.push(s);
  else
    for (let s = t; s > n; s += r)
      o.push(s);
  return o;
}
const xn = D(As, {
  props: ["config"]
});
function As(e) {
  const { fkey: t, tsGroup: n = {} } = e.config, r = ne(), s = Ts(t ?? "index"), i = Ds(e.config, r);
  return Kr(e.config, i), () => {
    const u = Qn(i.value, (...l) => {
      const d = l[0], a = l[2] !== void 0, c = a ? l[2] : l[1], f = a ? l[1] : c, h = s(d, c);
      return x(Cs, {
        key: h,
        vforValue: d,
        vforIndex: c,
        vforKeyValue: f,
        vforConfig: e.config
      });
    });
    return n && Object.keys(n).length > 0 ? x(Jt, n, {
      default: () => u
    }) : u;
  };
}
const $s = (e) => e, xs = (e, t) => t;
function Ts(e) {
  const t = gr(e);
  return typeof t == "function" ? t : e === "item" ? $s : xs;
}
function Ds(e, t) {
  const { type: n, value: r } = e.array, o = n === nt.range;
  if (n === nt.const || o && typeof r == "number") {
    const i = o ? Gt({
      end: Math.max(0, r)
    }) : r;
    return ie(() => ({
      get() {
        return i;
      },
      set() {
        throw new Error("Cannot set value to constant array");
      }
    }));
  }
  if (o) {
    const i = r, u = t.getVueRefObject(i);
    return ie(() => ({
      get() {
        return Gt({
          end: Math.max(0, u.value)
        });
      },
      set() {
        throw new Error("Cannot set value to range array");
      }
    }));
  }
  return ie(() => {
    const i = t.getVueRefObject(
      r
    );
    return {
      get() {
        return i.value;
      },
      set(u) {
        i.value = u;
      }
    };
  });
}
const Tn = D(js, {
  props: ["config"]
});
function js(e) {
  const { sid: t, items: n, on: r } = e.config;
  Re(t) && de(t);
  const o = ne();
  return () => (typeof r == "boolean" ? r : o.getValue(r)) ? n.map((i) => fe(i)) : void 0;
}
const Ht = D(Ms, {
  props: ["slotConfig"]
});
function Ms(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Re(t) && de(t), () => n.map((r) => fe(r));
}
const Qe = ":default", Dn = D(Ws, {
  props: ["config"]
});
function Ws(e) {
  const { on: t, caseValues: n, slots: r, sid: o } = e.config;
  Re(o) && de(o);
  const s = ne();
  return () => {
    const i = s.getValue(t), u = n.map((l, d) => {
      const a = d.toString(), c = r[a];
      return l === i ? x(Ht, { slotConfig: c, key: a }) : null;
    }).filter(Boolean);
    return u.length === 0 && Qe in r ? x(Ht, {
      slotConfig: r[Qe],
      key: Qe
    }) : u;
  };
}
const Bs = "on:mounted";
function Ls(e, t, n) {
  const r = Object.assign(
    {},
    ...Object.entries(t ?? {}).map(([i, u]) => {
      const l = u.map((d) => {
        if (d.type === "web") {
          const a = Fs(d, n);
          return Us(d, a, n);
        } else {
          if (d.type === "vue")
            return Hs(d, n);
          if (d.type === "js")
            return Gs(d, n);
        }
        throw new Error(`unknown event type ${d}`);
      });
      return { [i]: l };
    })
  ), { [Bs]: o, ...s } = r;
  if (e = Ne(e, s), o) {
    const i = (...l) => o.map(async (d) => {
      await d(...l);
    }), u = (...l) => Promise.all(i(...l));
    e = Yt(e, [
      [
        {
          mounted(l) {
            u(l);
          }
        }
      ]
    ]);
  }
  return e;
}
function Fs(e, t) {
  const { inputs: n = [] } = e;
  return (...r) => n.map(({ value: o, type: s }) => {
    if (s === H.EventContext) {
      const { path: i } = o;
      if (i.startsWith(":")) {
        const u = i.slice(1);
        return B(u)(...r);
      }
      return Fr(r[0], i.split("."));
    }
    return s === H.Ref ? t.getValue(o) : o;
  });
}
function Us(e, t, n) {
  async function r(...o) {
    const s = t(...o), i = cn({
      config: e.preSetup,
      varGetter: n
    });
    try {
      i.run();
      const u = await an().eventSend(e, s);
      if (!u)
        return;
      xe(u, e.sets, n);
    } finally {
      i.tryReset();
    }
  }
  return r;
}
function Gs(e, t) {
  const { sets: n, code: r, inputs: o = [] } = e, s = B(r);
  function i(...u) {
    const l = o.map(({ value: a, type: c }) => {
      if (c === H.EventContext) {
        if (a.path.startsWith(":")) {
          const f = a.path.slice(1);
          return B(f)(...u);
        }
        return Lr(u[0], a.path.split("."));
      }
      if (c === H.Ref)
        return ln(t.getValue(a));
      if (c === H.Data)
        return a;
      if (c === H.JsFn)
        return t.getValue(a);
      throw new Error(`unknown input type ${c}`);
    }), d = s(...l);
    if (n !== void 0) {
      const c = n.length === 1 ? [d] : d, f = c.map((h) => h === void 0 ? 1 : 0);
      xe(
        { values: c, types: f },
        n,
        t
      );
    }
  }
  return i;
}
function Hs(e, t) {
  const { code: n, inputs: r = {} } = e, o = Te(
    r,
    (u) => u.type !== H.Data ? t.getVueRefObject(u.value) : u.value
  ), s = B(n, o);
  function i(...u) {
    s(...u);
  }
  return i;
}
function Ks(e, t) {
  const n = [];
  (e.bStyle || []).forEach((s) => {
    Array.isArray(s) ? n.push(
      ...s.map((i) => t.getValue(i))
    ) : n.push(
      Te(
        s,
        (i) => t.getValue(i)
      )
    );
  });
  const r = Jn([e.style || {}, n]);
  return {
    hasStyle: r && Object.keys(r).length > 0,
    styles: r
  };
}
function zs(e, t) {
  const n = e.classes;
  if (!n)
    return null;
  if (typeof n == "string")
    return Ve(n);
  const { str: r, map: o, bind: s } = n, i = [];
  return r && i.push(r), o && i.push(
    Te(
      o,
      (u) => t.getValue(u)
    )
  ), s && i.push(...s.map((u) => t.getValue(u))), Ve(i);
}
function Ae(e, t = !0) {
  if (!(typeof e != "object" || e === null)) {
    if (Array.isArray(e)) {
      t && e.forEach((n) => Ae(n, !0));
      return;
    }
    for (const [n, r] of Object.entries(e))
      if (n.startsWith(":"))
        try {
          e[n.slice(1)] = new Function(`return (${r})`)(), delete e[n];
        } catch (o) {
          console.error(
            `Error while converting ${n} attribute to function:`,
            o
          );
        }
      else
        t && Ae(r, !0);
  }
}
function qs(e, t) {
  const n = e.startsWith(":");
  return n && (e = e.slice(1), t = B(t)), { name: e, value: t, isFunc: n };
}
function Qs(e, t, n) {
  var o;
  const r = {};
  return Pt(e.bProps || {}, (s, i) => {
    const u = n.getValue(s);
    be(u) || (Ae(u), r[i] = Js(u, i));
  }), (o = e.proxyProps) == null || o.forEach((s) => {
    const i = n.getValue(s);
    typeof i == "object" && Pt(i, (u, l) => {
      const { name: d, value: a } = qs(l, u);
      r[d] = a;
    });
  }), { ...t, ...r };
}
function Js(e, t) {
  return t === "innerText" ? $e(e) : e;
}
const Ys = D(Xs, {
  props: ["slotPropValue", "config"]
});
function Xs(e) {
  const { sid: t, items: n } = e.config, r = Re(t) ? de(t, {
    initSlotPropInfo: {
      value: e.slotPropValue
    }
  }).updateSlotPropValue : Zs;
  return () => (r({ sid: t, value: e.slotPropValue }), n.map((o) => fe(o)));
}
function Zs() {
}
function ei(e, t) {
  if (!e.slots)
    return null;
  const n = e.slots ?? {};
  return t ? ft(n[":"]) : un(n, { keyFn: (i) => i === ":" ? "default" : i, valueFn: (i) => (u) => i.use_prop ? ti(u, i) : ft(i) });
}
function ti(e, t) {
  return x(Ys, { config: t, slotPropValue: e });
}
function ni(e, t, n) {
  const r = [], { dir: o = [] } = t;
  return o.forEach((s) => {
    const { sys: i, name: u, arg: l, value: d, mf: a } = s;
    if (u === "vmodel") {
      const c = n.getVueRefObject(d);
      if (e = Ne(e, {
        [`onUpdate:${l}`]: (f) => {
          c.value = f;
        }
      }), i === 1) {
        const f = a ? Object.fromEntries(a.map((h) => [h, !0])) : {};
        r.push([Yn, c.value, void 0, f]);
      } else
        e = Ne(e, {
          [l]: c.value
        });
    } else if (u === "vshow") {
      const c = n.getVueRefObject(d);
      r.push([Xn, c.value]);
    } else
      console.warn(`Directive ${u} is not supported yet`);
  }), Yt(e, r);
}
function ri(e, t, n) {
  const { eRef: r } = t;
  return r ? Ne(e, { ref: n.getVueRefObject(r) }) : e;
}
const jn = Symbol();
function oi(e) {
  ae(jn, e);
}
function Vi() {
  return z(jn);
}
const si = D(ii, {
  props: ["config"]
});
function ii(e) {
  const { config: t } = e, n = ne({
    sidCollector: new ai(t).getCollectInfo()
  });
  t.varGetterStrategy && oi(n);
  const r = t.props ?? {};
  return Ae(r, !0), () => {
    const { tag: o } = t, s = typeof o == "string" ? o : n.getValue(o), i = Zn(s), u = typeof i == "string", l = zs(t, n), { styles: d, hasStyle: a } = Ks(t, n), c = ei(t, u), f = Qs(t, r, n), h = er(f) || {};
    a && (h.style = d), l && (h.class = l);
    let g = x(i, { ...h }, c);
    return g = Ls(g, t.events ?? {}, n), g = ri(g, t, n), ni(g, t, n);
  };
}
class ai {
  constructor(t) {
    $(this, "sids", /* @__PURE__ */ new Set());
    $(this, "needRouteParams", !0);
    $(this, "needRouter", !0);
    this.config = t;
  }
  /**
   * getCollectFn
   */
  getCollectInfo() {
    const {
      eRef: t,
      dir: n,
      classes: r,
      bProps: o,
      proxyProps: s,
      bStyle: i,
      events: u,
      varGetterStrategy: l
    } = this.config;
    if (l !== "all") {
      if (t && this._tryExtractSidToCollection(t), n && n.forEach((d) => {
        this._tryExtractSidToCollection(d.value), this._extendWithPaths(d.value);
      }), r && typeof r != "string") {
        const { map: d, bind: a } = r;
        d && Object.values(d).forEach((c) => {
          this._tryExtractSidToCollection(c), this._extendWithPaths(c);
        }), a && a.forEach((c) => {
          this._tryExtractSidToCollection(c), this._extendWithPaths(c);
        });
      }
      return o && Object.values(o).forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), s && s.forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), i && i.forEach((d) => {
        Array.isArray(d) ? d.forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        }) : Object.values(d).forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        });
      }), u && Object.values(u).forEach((d) => {
        this._handleEventInputs(d), this._handleEventSets(d);
      }), Array.isArray(l) && l.forEach((d) => {
        this.sids.add(d.sid);
      }), {
        sids: this.sids,
        needRouteParams: this.needRouteParams,
        needRouter: this.needRouter
      };
    }
  }
  _tryExtractSidToCollection(t) {
    on(t) && this.sids.add(t.sid);
  }
  _handleEventInputs(t) {
    t.forEach((n) => {
      if (n.type === "js" || n.type === "web") {
        const { inputs: r } = n;
        r == null || r.forEach((o) => {
          if (o.type === H.Ref) {
            const s = o.value;
            this._tryExtractSidToCollection(s), this._extendWithPaths(s);
          }
        });
      } else if (n.type === "vue") {
        const { inputs: r } = n;
        if (r) {
          const o = Object.values(r);
          o == null || o.forEach((s) => {
            if (s.type === H.Ref) {
              const i = s.value;
              this._tryExtractSidToCollection(i), this._extendWithPaths(i);
            }
          });
        }
      }
    });
  }
  _handleEventSets(t) {
    t.forEach((n) => {
      if (n.type === "js" || n.type === "web") {
        const { sets: r } = n;
        r == null || r.forEach((o) => {
          pt(o.ref) && (this.sids.add(o.ref.sid), this._extendWithPaths(o.ref));
        });
      }
    });
  }
  _extendWithPaths(t) {
    if (!t.path)
      return;
    const n = [];
    for (n.push(...t.path); n.length > 0; ) {
      const r = n.pop();
      if (r === void 0)
        break;
      if (vr(r)) {
        const o = yr(r);
        this._tryExtractSidToCollection(o), o.path && n.push(...o.path);
      }
    }
  }
}
function fe(e, t) {
  return Pr(e) ? x(xn, { config: e, key: t }) : Sr(e) ? x(Tn, { config: e, key: t }) : Or(e) ? x(Dn, { config: e, key: t }) : x(si, { config: e, key: t });
}
function ft(e, t) {
  return x(Mn, { slotConfig: e, key: t });
}
const Mn = D(ci, {
  props: ["slotConfig"]
});
function ci(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Re(t) && de(t), () => n.map((r) => fe(r));
}
function ui(e, t) {
  const { state: n, isReady: r, isLoading: o } = pr(async () => {
    let s = e;
    const i = t;
    if (!s && !i)
      throw new Error("Either config or configUrl must be provided");
    if (!s && i && (s = await (await fetch(i)).json()), !s)
      throw new Error("Failed to load config");
    return s;
  }, {});
  return { config: n, isReady: r, isLoading: o };
}
function li(e) {
  const t = J(!1), n = J("");
  function r(o, s) {
    let i;
    return s.component ? i = `Error captured from component:tag: ${s.component.tag} ; id: ${s.component.id} ` : i = "Error captured from app init", console.group(i), console.error("Component:", s.component), console.error("Error:", o), console.groupEnd(), e && (t.value = !0, n.value = `${i} ${o.message}`), !1;
  }
  return tr(r), { hasError: t, errorMessage: n };
}
const fi = {
  class: "app-box insta-themes",
  "data-scaling": "100%"
}, di = {
  key: 0,
  style: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
}, hi = {
  key: 0,
  style: { color: "red", "font-size": "1.2em", margin: "1rem", border: "1px dashed red", padding: "1rem" }
}, pi = /* @__PURE__ */ D({
  __name: "App",
  props: {
    config: {},
    meta: {},
    configUrl: {}
  },
  setup(e) {
    const t = e, { debug: n = !1 } = t.meta, { config: r, isLoading: o } = ui(
      t.config,
      t.configUrl
    );
    K(r, (u) => {
      u.url && (lr({
        mode: t.meta.mode,
        version: t.meta.version,
        queryPath: u.url.path,
        pathParams: u.url.params,
        webServerInfo: u.webInfo
      }), Ir(t.meta.mode)), fr(u);
    });
    const { hasError: s, errorMessage: i } = li(n);
    return (u, l) => (se(), ve("div", fi, [
      M(o) ? (se(), ve("div", di, l[0] || (l[0] = [
        nr("p", { style: { margin: "auto" } }, "Loading ...", -1)
      ]))) : (se(), ve("div", {
        key: 1,
        class: Ve(["insta-main", M(r).class])
      }, [
        rr(M(Mn), { "slot-config": M(r) }, null, 8, ["slot-config"]),
        M(s) ? (se(), ve("div", hi, $e(M(i)), 1)) : or("", !0)
      ], 2))
    ]));
  }
});
function gi(e, { slots: t }) {
  const { name: n = "fade", tag: r } = e;
  return () => x(
    Jt,
    { name: n, tag: r },
    {
      default: t.default
    }
  );
}
const mi = D(gi, {
  props: ["name", "tag"]
});
function vi(e) {
  const { content: t, r: n = 0 } = e, r = ne(), o = n === 1 ? () => r.getValue(t) : () => t;
  return () => $e(o());
}
const yi = D(vi, {
  props: ["content", "r"]
});
function Ei(e) {
  return `i-size-${e}`;
}
function _i(e) {
  return e ? `i-weight-${e}` : "";
}
function wi(e) {
  return e ? `i-text-align-${e}` : "";
}
const bi = /* @__PURE__ */ D({
  __name: "Heading",
  props: {
    text: {},
    size: {},
    weight: {},
    align: {}
  },
  setup(e) {
    const t = e, n = W(() => [
      Ei(t.size ?? "6"),
      _i(t.weight),
      wi(t.align)
    ]);
    return (r, o) => (se(), ve("h1", {
      class: Ve(["insta-Heading", n.value])
    }, $e(r.text), 3));
  }
}), Ri = /* @__PURE__ */ D({
  __name: "_Teleport",
  props: {
    to: {},
    defer: { type: Boolean, default: !0 },
    disabled: { type: Boolean, default: !1 }
  },
  setup(e) {
    return (t, n) => (se(), sr(ir, {
      to: t.to,
      defer: t.defer,
      disabled: t.disabled
    }, [
      ar(t.$slots, "default")
    ], 8, ["to", "defer", "disabled"]));
  }
});
function Pi(e) {
  if (!e.router)
    throw new Error("Router config is not provided.");
  const { routes: t, kAlive: n = !1 } = e.router;
  return t.map(
    (o) => Wn(o, n)
  );
}
function Wn(e, t) {
  var u;
  const { server: n = !1, vueItem: r } = e, o = () => {
    if (n)
      throw new Error("Server-side rendering is not supported yet.");
    return Promise.resolve(Si(e, t));
  }, s = (u = r.children) == null ? void 0 : u.map(
    (l) => Wn(l, t)
  ), i = {
    ...r,
    children: s,
    component: o
  };
  return r.component.length === 0 && delete i.component, s === void 0 && delete i.children, i;
}
function Si(e, t) {
  const { sid: n, vueItem: r } = e, { path: o, component: s } = r, i = ft(
    {
      items: s,
      sid: n
    },
    o
  ), u = x(cr, null, i);
  return t ? x(ur, null, () => i) : u;
}
function Oi(e, t) {
  const { mode: n = "hash" } = t.router, r = n === "hash" ? Io() : n === "memory" ? Co() : bn();
  e.use(
    ws({
      history: r,
      routes: Pi(t)
    })
  );
}
function Ci(e, t) {
  e.component("insta-ui", pi), e.component("vif", Tn), e.component("vfor", xn), e.component("match", Dn), e.component("teleport", Ri), e.component("ts-group", mi), e.component("content", yi), e.component("heading", bi), t.router && Oi(e, t);
}
export {
  Ae as convertDynamicProperties,
  Ci as install,
  Vi as useVarGetter
};
//# sourceMappingURL=insta-ui.js.map
