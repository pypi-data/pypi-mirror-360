from sci_research.lmp_use.lmp_calculation_and_deal_data.He_incidence_Non_accumulative import fit_paras
import importlib

importlib.reload(fit_paras)
fp = fit_paras.Practice3()
fp.train()