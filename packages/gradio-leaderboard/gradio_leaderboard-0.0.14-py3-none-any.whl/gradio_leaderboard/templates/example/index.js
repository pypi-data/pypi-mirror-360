const {
  SvelteComponent: j,
  append_hydration: y,
  attr: b,
  children: g,
  claim_element: d,
  claim_space: w,
  claim_text: I,
  destroy_each: V,
  detach: a,
  element: m,
  empty: p,
  ensure_array_like: v,
  get_svelte_dataset: z,
  init: F,
  insert_hydration: h,
  listen: E,
  noop: k,
  run_all: G,
  safe_not_equal: H,
  space: B,
  text: L,
  toggle_class: o
} = window.__gradio__svelte__internal;
function q(f, e, l) {
  const t = f.slice();
  return t[9] = e[l], t[11] = l, t;
}
function C(f, e, l) {
  const t = f.slice();
  return t[12] = e[l], t[14] = l, t;
}
function J(f) {
  let e, l, t;
  function i(s, n) {
    return typeof /*loaded_value*/
    s[5] == "string" ? M : K;
  }
  let c = i(f)(f);
  return {
    c() {
      e = m("div"), c.c(), this.h();
    },
    l(s) {
      e = d(s, "DIV", { class: !0 });
      var n = g(e);
      c.l(n), n.forEach(a), this.h();
    },
    h() {
      b(e, "class", "svelte-1bq8l1x"), o(
        e,
        "table",
        /*type*/
        f[1] === "table"
      ), o(
        e,
        "gallery",
        /*type*/
        f[1] === "gallery"
      ), o(
        e,
        "selected",
        /*selected*/
        f[2]
      );
    },
    m(s, n) {
      h(s, e, n), c.m(e, null), l || (t = [
        E(
          e,
          "mouseenter",
          /*mouseenter_handler*/
          f[7]
        ),
        E(
          e,
          "mouseleave",
          /*mouseleave_handler*/
          f[8]
        )
      ], l = !0);
    },
    p(s, n) {
      c.p(s, n), n & /*type*/
      2 && o(
        e,
        "table",
        /*type*/
        s[1] === "table"
      ), n & /*type*/
      2 && o(
        e,
        "gallery",
        /*type*/
        s[1] === "gallery"
      ), n & /*selected*/
      4 && o(
        e,
        "selected",
        /*selected*/
        s[2]
      );
    },
    d(s) {
      s && a(e), c.d(), l = !1, G(t);
    }
  };
}
function K(f) {
  let e, l, t = v(
    /*loaded_value*/
    f[5].slice(0, 3)
  ), i = [];
  for (let c = 0; c < t.length; c += 1)
    i[c] = T(q(f, t, c));
  let r = (
    /*value*/
    f[0].length > 3 && A(f)
  );
  return {
    c() {
      e = m("table");
      for (let c = 0; c < i.length; c += 1)
        i[c].c();
      l = B(), r && r.c(), this.h();
    },
    l(c) {
      e = d(c, "TABLE", { class: !0 });
      var s = g(e);
      for (let n = 0; n < i.length; n += 1)
        i[n].l(s);
      l = w(s), r && r.l(s), s.forEach(a), this.h();
    },
    h() {
      b(e, "class", " svelte-1bq8l1x");
    },
    m(c, s) {
      h(c, e, s);
      for (let n = 0; n < i.length; n += 1)
        i[n] && i[n].m(e, null);
      y(e, l), r && r.m(e, null);
    },
    p(c, s) {
      if (s & /*loaded_value*/
      32) {
        t = v(
          /*loaded_value*/
          c[5].slice(0, 3)
        );
        let n;
        for (n = 0; n < t.length; n += 1) {
          const u = q(c, t, n);
          i[n] ? i[n].p(u, s) : (i[n] = T(u), i[n].c(), i[n].m(e, l));
        }
        for (; n < i.length; n += 1)
          i[n].d(1);
        i.length = t.length;
      }
      /*value*/
      c[0].length > 3 ? r ? r.p(c, s) : (r = A(c), r.c(), r.m(e, null)) : r && (r.d(1), r = null);
    },
    d(c) {
      c && a(e), V(i, c), r && r.d();
    }
  };
}
function M(f) {
  let e;
  return {
    c() {
      e = L(
        /*loaded_value*/
        f[5]
      );
    },
    l(l) {
      e = I(
        l,
        /*loaded_value*/
        f[5]
      );
    },
    m(l, t) {
      h(l, e, t);
    },
    p: k,
    d(l) {
      l && a(e);
    }
  };
}
function D(f) {
  let e, l = (
    /*cell*/
    f[12] + ""
  ), t;
  return {
    c() {
      e = m("td"), t = L(l), this.h();
    },
    l(i) {
      e = d(i, "TD", { class: !0 });
      var r = g(e);
      t = I(r, l), r.forEach(a), this.h();
    },
    h() {
      b(e, "class", "svelte-1bq8l1x");
    },
    m(i, r) {
      h(i, e, r), y(e, t);
    },
    p: k,
    d(i) {
      i && a(e);
    }
  };
}
function N(f) {
  let e, l = "…";
  return {
    c() {
      e = m("td"), e.textContent = l, this.h();
    },
    l(t) {
      e = d(t, "TD", { class: !0, "data-svelte-h": !0 }), z(e) !== "svelte-1o35md4" && (e.textContent = l), this.h();
    },
    h() {
      b(e, "class", "svelte-1bq8l1x");
    },
    m(t, i) {
      h(t, e, i);
    },
    d(t) {
      t && a(e);
    }
  };
}
function T(f) {
  let e, l, t = v(
    /*row*/
    f[9].slice(0, 3)
  ), i = [];
  for (let c = 0; c < t.length; c += 1)
    i[c] = D(C(f, t, c));
  let r = (
    /*row*/
    f[9].length > 3 && N()
  );
  return {
    c() {
      e = m("tr");
      for (let c = 0; c < i.length; c += 1)
        i[c].c();
      l = B(), r && r.c();
    },
    l(c) {
      e = d(c, "TR", {});
      var s = g(e);
      for (let n = 0; n < i.length; n += 1)
        i[n].l(s);
      l = w(s), r && r.l(s), s.forEach(a);
    },
    m(c, s) {
      h(c, e, s);
      for (let n = 0; n < i.length; n += 1)
        i[n] && i[n].m(e, null);
      y(e, l), r && r.m(e, null);
    },
    p(c, s) {
      if (s & /*loaded_value*/
      32) {
        t = v(
          /*row*/
          c[9].slice(0, 3)
        );
        let n;
        for (n = 0; n < t.length; n += 1) {
          const u = C(c, t, n);
          i[n] ? i[n].p(u, s) : (i[n] = D(u), i[n].c(), i[n].m(e, l));
        }
        for (; n < i.length; n += 1)
          i[n].d(1);
        i.length = t.length;
      }
    },
    d(c) {
      c && a(e), V(i, c), r && r.d();
    }
  };
}
function A(f) {
  let e;
  return {
    c() {
      e = m("div"), this.h();
    },
    l(l) {
      e = d(l, "DIV", { class: !0 }), g(e).forEach(a), this.h();
    },
    h() {
      b(e, "class", "overlay svelte-1bq8l1x"), o(
        e,
        "odd",
        /*index*/
        f[3] % 2 != 0
      ), o(
        e,
        "even",
        /*index*/
        f[3] % 2 == 0
      ), o(
        e,
        "button",
        /*type*/
        f[1] === "gallery"
      );
    },
    m(l, t) {
      h(l, e, t);
    },
    p(l, t) {
      t & /*index*/
      8 && o(
        e,
        "odd",
        /*index*/
        l[3] % 2 != 0
      ), t & /*index*/
      8 && o(
        e,
        "even",
        /*index*/
        l[3] % 2 == 0
      ), t & /*type*/
      2 && o(
        e,
        "button",
        /*type*/
        l[1] === "gallery"
      );
    },
    d(l) {
      l && a(e);
    }
  };
}
function O(f) {
  let e, l = (
    /*loaded*/
    f[6] && J(f)
  );
  return {
    c() {
      l && l.c(), e = p();
    },
    l(t) {
      l && l.l(t), e = p();
    },
    m(t, i) {
      l && l.m(t, i), h(t, e, i);
    },
    p(t, [i]) {
      /*loaded*/
      t[6] && l.p(t, i);
    },
    i: k,
    o: k,
    d(t) {
      t && a(e), l && l.d(t);
    }
  };
}
function P(f, e, l) {
  let { value: t } = e, { type: i } = e, { selected: r = !1 } = e, { index: c } = e, s = !1, n = t, u = Array.isArray(n);
  const R = () => l(4, s = !0), S = () => l(4, s = !1);
  return f.$$set = (_) => {
    "value" in _ && l(0, t = _.value), "type" in _ && l(1, i = _.type), "selected" in _ && l(2, r = _.selected), "index" in _ && l(3, c = _.index);
  }, [
    t,
    i,
    r,
    c,
    s,
    n,
    u,
    R,
    S
  ];
}
class Q extends j {
  constructor(e) {
    super(), F(this, e, P, O, H, { value: 0, type: 1, selected: 2, index: 3 });
  }
}
export {
  Q as default
};
