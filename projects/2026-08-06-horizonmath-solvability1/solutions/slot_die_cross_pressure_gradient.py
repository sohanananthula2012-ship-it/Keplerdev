def proposed_solution(lam_tilde, n, pi_q):
    from mpmath import mp, mpf
    mp.dps = 80
    lam = mpf(lam_tilde); n = mpf(n); pi_q = mpf(pi_q)
    quad_degree = 40
    nodes_raw, weights_raw = mp.gauss_quadrature(quad_degree, "legendre")
    eta_nodes = [(x + 1) / 2 for x in nodes_raw]
    eta_weights = [w / 2 for w in weights_raw]
    def shear_from_stress(tau):
        if tau <= 0: return mpf(0)
        def residual(q): return q / (1 + (lam * q) ** (1 - n)) - tau
        hi = mp.mpf(1) if tau < 1 else tau + 1
        while residual(hi) < 0: hi *= 2
        return mp.findroot(residual, (mpf(0), hi), solver="anderson")
    def system(log_tau0, log_tau1):
        tau0 = mp.exp(log_tau0); tau1 = mp.exp(log_tau1)
        shears = [shear_from_stress(tau0 + (tau1 - tau0) * e) for e in eta_nodes]
        endpoint_gap = sum(w * s for w, s in zip(eta_weights, shears)) - 1
        flux = -1 + sum(w * (1 - e) * s for w, e, s in zip(eta_weights, eta_nodes, shears)) - pi_q
        return endpoint_gap, flux
    sol = mp.findroot(system, (mpf(0), mpf(0)), solver="mnewton")
    v = mp.exp(sol[1]) - mp.exp(sol[0])
    return mpf(mp.nstr(v, 20))   # report at the 20-sig precision of the ground truth
