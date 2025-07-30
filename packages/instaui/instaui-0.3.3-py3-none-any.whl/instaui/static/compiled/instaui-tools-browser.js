import { shallowRef as T, shallowReadonly as re, toValue as A, getCurrentScope as ae, onScopeDispose as ie, watch as x, toRef as ue, readonly as K, ref as Q, customRef as se, onMounted as $, nextTick as q, getCurrentInstance as V, hasInjectionContext as U, inject as le, computed as M, unref as ce, watchEffect as fe, toRaw as de } from "vue";
function X(e) {
  return ae() ? (ie(e), !0) : !1;
}
const z = /* @__PURE__ */ new WeakMap(), pe = (...e) => {
  var t;
  const n = e[0], o = (t = V()) == null ? void 0 : t.proxy;
  if (o == null && !U())
    throw new Error("injectLocal must be called in setup");
  return o && z.has(o) && n in z.get(o) ? z.get(o)[n] : le(...e);
}, J = typeof window < "u" && typeof document < "u";
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const me = Object.prototype.toString, ve = (e) => me.call(e) === "[object Object]", he = () => {
};
function Y(...e) {
  if (e.length !== 1)
    return ue(...e);
  const t = e[0];
  return typeof t == "function" ? K(se(() => ({ get: t, set: he }))) : Q(t);
}
function ye(e, t) {
  function n(...o) {
    return new Promise((a, c) => {
      Promise.resolve(e(() => t.apply(this, o), { fn: t, thisArg: this, args: o })).then(a).catch(c);
    });
  }
  return n;
}
const Z = (e) => e();
function ge(e = Z, t = {}) {
  const {
    initialState: n = "active"
  } = t, o = Y(n === "active");
  function a() {
    o.value = !1;
  }
  function c() {
    o.value = !0;
  }
  const u = (...r) => {
    o.value && e(...r);
  };
  return { isActive: K(o), pause: a, resume: c, eventFilter: u };
}
function Se(e) {
  let t;
  function n() {
    return t || (t = e()), t;
  }
  return n.reset = async () => {
    const o = t;
    t = void 0, o && await o;
  }, n;
}
function I(e) {
  return e.endsWith("rem") ? Number.parseFloat(e) * 16 : Number.parseFloat(e);
}
function P(e) {
  return Array.isArray(e) ? e : [e];
}
function we(e) {
  return V();
}
function be(e, t, n = {}) {
  const {
    eventFilter: o = Z,
    ...a
  } = n;
  return x(
    e,
    ye(
      o,
      t
    ),
    a
  );
}
function Ce(e, t, n = {}) {
  const {
    eventFilter: o,
    initialState: a = "active",
    ...c
  } = n, { eventFilter: u, pause: r, resume: s, isActive: l } = ge(o, { initialState: a });
  return { stop: be(
    e,
    t,
    {
      ...c,
      eventFilter: u
    }
  ), pause: r, resume: s, isActive: l };
}
function ee(e, t = !0, n) {
  we() ? $(e, n) : t ? e() : q(e);
}
function ke(e, t, n = {}) {
  const {
    immediate: o = !0,
    immediateCallback: a = !1
  } = n, c = T(!1);
  let u = null;
  function r() {
    u && (clearTimeout(u), u = null);
  }
  function s() {
    c.value = !1, r();
  }
  function l(...f) {
    a && e(), r(), c.value = !0, u = setTimeout(() => {
      c.value = !1, u = null, e(...f);
    }, A(t));
  }
  return o && (c.value = !0, J && l()), X(s), {
    isPending: re(c),
    start: l,
    stop: s
  };
}
function Te(e, t, n) {
  return x(
    e,
    t,
    {
      ...n,
      immediate: !0
    }
  );
}
const F = J ? window : void 0, te = J ? window.navigator : void 0;
function ne(e) {
  var t;
  const n = A(e);
  return (t = n == null ? void 0 : n.$el) != null ? t : n;
}
function L(...e) {
  const t = [], n = () => {
    t.forEach((r) => r()), t.length = 0;
  }, o = (r, s, l, f) => (r.addEventListener(s, l, f), () => r.removeEventListener(s, l, f)), a = M(() => {
    const r = P(A(e[0])).filter((s) => s != null);
    return r.every((s) => typeof s != "string") ? r : void 0;
  }), c = Te(
    () => {
      var r, s;
      return [
        (s = (r = a.value) == null ? void 0 : r.map((l) => ne(l))) != null ? s : [F].filter((l) => l != null),
        P(A(a.value ? e[1] : e[0])),
        P(ce(a.value ? e[2] : e[1])),
        // @ts-expect-error - TypeScript gets the correct types, but somehow still complains
        A(a.value ? e[3] : e[2])
      ];
    },
    ([r, s, l, f]) => {
      if (n(), !(r != null && r.length) || !(s != null && s.length) || !(l != null && l.length))
        return;
      const v = ve(f) ? { ...f } : f;
      t.push(
        ...r.flatMap(
          (k) => s.flatMap(
            (S) => l.map((h) => o(k, S, h, v))
          )
        )
      );
    },
    { flush: "post" }
  ), u = () => {
    c(), n();
  };
  return X(n), u;
}
function Ae() {
  const e = T(!1), t = V();
  return t && $(() => {
    e.value = !0;
  }, t), e;
}
function B(e) {
  const t = Ae();
  return M(() => (t.value, !!e()));
}
const Me = Symbol("vueuse-ssr-width");
function Ee() {
  const e = U() ? pe(Me, null) : null;
  return typeof e == "number" ? e : void 0;
}
function Oe(e, t = {}) {
  const { window: n = F, ssrWidth: o = Ee() } = t, a = B(() => n && "matchMedia" in n && typeof n.matchMedia == "function"), c = T(typeof o == "number"), u = T(), r = T(!1), s = (l) => {
    r.value = l.matches;
  };
  return fe(() => {
    if (c.value) {
      c.value = !a.value;
      const l = A(e).split(",");
      r.value = l.some((f) => {
        const v = f.includes("not all"), k = f.match(/\(\s*min-width:\s*(-?\d+(?:\.\d*)?[a-z]+\s*)\)/), S = f.match(/\(\s*max-width:\s*(-?\d+(?:\.\d*)?[a-z]+\s*)\)/);
        let h = !!(k || S);
        return k && h && (h = o >= I(k[1])), S && h && (h = o <= I(S[1])), v ? !h : h;
      });
      return;
    }
    a.value && (u.value = n.matchMedia(A(e)), r.value = u.value.matches);
  }), L(u, "change", s, { passive: !0 }), M(() => r.value);
}
function H(e, t = {}) {
  const {
    controls: n = !1,
    navigator: o = te
  } = t, a = B(() => o && "permissions" in o), c = T(), u = typeof e == "string" ? { name: e } : e, r = T(), s = () => {
    var f, v;
    r.value = (v = (f = c.value) == null ? void 0 : f.state) != null ? v : "prompt";
  };
  L(c, "change", s, { passive: !0 });
  const l = Se(async () => {
    if (a.value) {
      if (!c.value)
        try {
          c.value = await o.permissions.query(u);
        } catch {
          c.value = void 0;
        } finally {
          s();
        }
      if (n)
        return de(c.value);
    }
  });
  return l(), n ? {
    state: r,
    isSupported: a,
    query: l
  } : r;
}
function ze(e = {}) {
  const {
    navigator: t = te,
    read: n = !1,
    source: o,
    copiedDuring: a = 1500,
    legacy: c = !1
  } = e, u = B(() => t && "clipboard" in t), r = H("clipboard-read"), s = H("clipboard-write"), l = M(() => u.value || c), f = T(""), v = T(!1), k = ke(() => v.value = !1, a, { immediate: !1 });
  async function S() {
    let d = !(u.value && b(r.value));
    if (!d)
      try {
        f.value = await t.clipboard.readText();
      } catch {
        d = !0;
      }
    d && (f.value = C());
  }
  l.value && n && L(["copy", "cut"], S, { passive: !0 });
  async function h(d = A(o)) {
    if (l.value && d != null) {
      let p = !(u.value && b(s.value));
      if (!p)
        try {
          await t.clipboard.writeText(d);
        } catch {
          p = !0;
        }
      p && w(d), f.value = d, v.value = !0, k.start();
    }
  }
  function w(d) {
    const p = document.createElement("textarea");
    p.value = d ?? "", p.style.position = "absolute", p.style.opacity = "0", document.body.appendChild(p), p.select(), document.execCommand("copy"), p.remove();
  }
  function C() {
    var d, p, y;
    return (y = (p = (d = document == null ? void 0 : document.getSelection) == null ? void 0 : d.call(document)) == null ? void 0 : p.toString()) != null ? y : "";
  }
  function b(d) {
    return d === "granted" || d === "prompt";
  }
  return {
    isSupported: l,
    text: f,
    copied: v,
    copy: h
  };
}
const R = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, D = "__vueuse_ssr_handlers__", We = /* @__PURE__ */ Ne();
function Ne() {
  return D in R || (R[D] = R[D] || {}), R[D];
}
function oe(e, t) {
  return We[e] || t;
}
function _e(e) {
  return Oe("(prefers-color-scheme: dark)", e);
}
function je(e) {
  return e == null ? "any" : e instanceof Set ? "set" : e instanceof Map ? "map" : e instanceof Date ? "date" : typeof e == "boolean" ? "boolean" : typeof e == "string" ? "string" : typeof e == "object" ? "object" : Number.isNaN(e) ? "any" : "number";
}
const Fe = {
  boolean: {
    read: (e) => e === "true",
    write: (e) => String(e)
  },
  object: {
    read: (e) => JSON.parse(e),
    write: (e) => JSON.stringify(e)
  },
  number: {
    read: (e) => Number.parseFloat(e),
    write: (e) => String(e)
  },
  any: {
    read: (e) => e,
    write: (e) => String(e)
  },
  string: {
    read: (e) => e,
    write: (e) => String(e)
  },
  map: {
    read: (e) => new Map(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e.entries()))
  },
  set: {
    read: (e) => new Set(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e))
  },
  date: {
    read: (e) => new Date(e),
    write: (e) => e.toISOString()
  }
}, G = "vueuse-storage";
function Le(e, t, n, o = {}) {
  var a;
  const {
    flush: c = "pre",
    deep: u = !0,
    listenToStorageChanges: r = !0,
    writeDefaults: s = !0,
    mergeDefaults: l = !1,
    shallow: f,
    window: v = F,
    eventFilter: k,
    onError: S = (i) => {
      console.error(i);
    },
    initOnMounted: h
  } = o, w = (f ? T : Q)(typeof t == "function" ? t() : t), C = M(() => A(e));
  if (!n)
    try {
      n = oe("getDefaultStorage", () => {
        var i;
        return (i = F) == null ? void 0 : i.localStorage;
      })();
    } catch (i) {
      S(i);
    }
  if (!n)
    return w;
  const b = A(t), d = je(b), p = (a = o.serializer) != null ? a : Fe[d], { pause: y, resume: O } = Ce(
    w,
    () => N(w.value),
    { flush: c, deep: u, eventFilter: k }
  );
  x(C, () => E(), { flush: c }), v && r && ee(() => {
    n instanceof Storage ? L(v, "storage", E, { passive: !0 }) : L(v, G, W), h && E();
  }), h || E();
  function _(i, m) {
    if (v) {
      const g = {
        key: C.value,
        oldValue: i,
        newValue: m,
        storageArea: n
      };
      v.dispatchEvent(n instanceof Storage ? new StorageEvent("storage", g) : new CustomEvent(G, {
        detail: g
      }));
    }
  }
  function N(i) {
    try {
      const m = n.getItem(C.value);
      if (i == null)
        _(m, null), n.removeItem(C.value);
      else {
        const g = p.write(i);
        m !== g && (n.setItem(C.value, g), _(m, g));
      }
    } catch (m) {
      S(m);
    }
  }
  function j(i) {
    const m = i ? i.newValue : n.getItem(C.value);
    if (m == null)
      return s && b != null && n.setItem(C.value, p.write(b)), b;
    if (!i && l) {
      const g = p.read(m);
      return typeof l == "function" ? l(g, b) : d === "object" && !Array.isArray(g) ? { ...b, ...g } : g;
    } else return typeof m != "string" ? m : p.read(m);
  }
  function E(i) {
    if (!(i && i.storageArea !== n)) {
      if (i && i.key == null) {
        w.value = b;
        return;
      }
      if (!(i && i.key !== C.value)) {
        y();
        try {
          (i == null ? void 0 : i.newValue) !== p.write(w.value) && (w.value = j(i));
        } catch (m) {
          S(m);
        } finally {
          i ? q(O) : O();
        }
      }
    }
  }
  function W(i) {
    E(i.detail);
  }
  return w;
}
const Re = "*,*::before,*::after{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}";
function De(e = {}) {
  const {
    selector: t = "html",
    attribute: n = "class",
    initialValue: o = "auto",
    window: a = F,
    storage: c,
    storageKey: u = "vueuse-color-scheme",
    listenToStorageChanges: r = !0,
    storageRef: s,
    emitAuto: l,
    disableTransition: f = !0
  } = e, v = {
    auto: "",
    light: "light",
    dark: "dark",
    ...e.modes || {}
  }, k = _e({ window: a }), S = M(() => k.value ? "dark" : "light"), h = s || (u == null ? Y(o) : Le(u, o, c, { window: a, listenToStorageChanges: r })), w = M(() => h.value === "auto" ? S.value : h.value), C = oe(
    "updateHTMLAttrs",
    (y, O, _) => {
      const N = typeof y == "string" ? a == null ? void 0 : a.document.querySelector(y) : ne(y);
      if (!N)
        return;
      const j = /* @__PURE__ */ new Set(), E = /* @__PURE__ */ new Set();
      let W = null;
      if (O === "class") {
        const m = _.split(/\s/g);
        Object.values(v).flatMap((g) => (g || "").split(/\s/g)).filter(Boolean).forEach((g) => {
          m.includes(g) ? j.add(g) : E.add(g);
        });
      } else
        W = { key: O, value: _ };
      if (j.size === 0 && E.size === 0 && W === null)
        return;
      let i;
      f && (i = a.document.createElement("style"), i.appendChild(document.createTextNode(Re)), a.document.head.appendChild(i));
      for (const m of j)
        N.classList.add(m);
      for (const m of E)
        N.classList.remove(m);
      W && N.setAttribute(W.key, W.value), f && (a.getComputedStyle(i).opacity, document.head.removeChild(i));
    }
  );
  function b(y) {
    var O;
    C(t, n, (O = v[y]) != null ? O : y);
  }
  function d(y) {
    e.onChanged ? e.onChanged(y, b) : b(y);
  }
  x(w, d, { flush: "post", immediate: !0 }), ee(() => d(w.value));
  const p = M({
    get() {
      return l ? h.value : w.value;
    },
    set(y) {
      h.value = y;
    }
  });
  return Object.assign(p, { store: h, system: S, state: w });
}
function Pe(e = {}) {
  const {
    valueDark: t = "dark",
    valueLight: n = ""
  } = e, o = De({
    ...e,
    onChanged: (u, r) => {
      var s;
      e.onChanged ? (s = e.onChanged) == null || s.call(e, u === "dark", r, u) : r(u);
    },
    modes: {
      dark: t,
      light: n
    }
  }), a = M(() => o.system.value);
  return M({
    get() {
      return o.value === "dark";
    },
    set(u) {
      const r = u ? "dark" : "light";
      a.value === r ? o.value = "auto" : o.value = r;
    }
  });
}
export {
  ze as useClipboard,
  Pe as useDark
};
