# Perpetuity

Perpetuity is a retirement simulator that implements an investment strategy based on the idea of a CD ladder.

An initial balance is used to fund one year of consumption and to purchase a CD ladder to the desired maturity. Any remaining money is invested. In each subsequent year, one CD matures and is treated as income while another CD is purchased using capital gains from the invested funds. If the strategy is executed successfully, a constant standard of living can be maintained while minimizing exposure to economic shocks. 

Run the `perpetuity` command to output results as CSV or use `perpetuity.simulation.Simulator` in your own program.
