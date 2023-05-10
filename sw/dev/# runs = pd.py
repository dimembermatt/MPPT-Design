# runs = pd.DataFrame(
#     columns=["R_L * 10", "SW_BUDGET", "TOT_LOSS", "F_SW (kHz * 100)"]
# )
# design = boost_converter.design_specs["DESIGN"]
# ind = design["inductor"]
# sw = design["switches"]
# iters = 0
# for j in np.arange(2.5, 2.3, -0.02):
#     sw["p_bud"] = j
#     for i in np.arange(0.2, 0.1, -0.01):
#         ind["r_l"] = i
#         print(f"ITERATION {iters} | P_SW_BUD: {j :.3f} | R_L: {i :.3f}", end='\r')
#         try:
#             boost_converter.iterate_design()
#             runs.loc[iters] = [
#                 ind["r_l"] * 1e1,
#                 sw["p_bud"],
#                 boost_converter.p_tot_loss,
#                 design["switches"]["f_sw"] * 1e-5
#             ]
#         except KeyboardInterrupt:
#             sys.exit()
#         except Exception as e:
#             print(e)
#         finally:
#             iters += 1

# ax = runs.plot(
#     y=["R_L * 10", "SW_BUDGET", "TOT_LOSS", "F_SW (kHz * 100)"],
#     use_index=True,
#     title="Optimization Iteration vs Device Worst Case Loss",
#     grid=True
# )
# ax.set_xlabel("Optimization Iteration")
# ax.set_ylabel("Power Dissipation, Predicted vs Budgeted (W)")
# plt.show()

# print(runs)

# print("Best run")
# print(runs.nsmallest(1, "TOT_LOSS"))
