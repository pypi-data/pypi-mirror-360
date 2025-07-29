import shnitsel as sh

# p = "/traj/SHNITSEL_alkenes/butene_combined"
p = "/traj/SHNITSEL_alkenes/traj_C2H4"

sh.parse.read_trajs(p, kind="sharc", parallel=True)
