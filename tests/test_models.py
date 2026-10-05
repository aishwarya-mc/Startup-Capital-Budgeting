"""Small exhaustive oracles and corruption tests, independent of model equations."""
import copy
import itertools
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from integer_programming import solve_portfolio
from goal_programming import solve_goal_portfolio
from portfolio_model import validate, load_data, config
from score_projects import funding_history_risk, strategic_alignment


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=pd.DataFrame({'project_id':['P003','P004','P005','P006'],
            'investment_cost':[2.,3.,1.,4.], 'investment_potential_score':[5.,6.,8.,9.],
            'risk_score':[80.,30.,60.,10.], 'strategic_score':[10.,100.,50.,0.]})

    def feasible(self,logic):
        for values in itertools.product([0,1],repeat=4):
            x=np.array(values)
            if self.df.investment_cost@x>5:
                continue
            if logic=='assumed_logic' and (x[2]>x[1] or x[0]+x[1]>1):
                continue
            yield x

    def test_ip_exhaustive_with_and_without_logic(self):
        for logic in ['baseline','assumed_logic']:
            expected=max(self.df.investment_potential_score@x for x in self.feasible(logic))
            actual=solve_portfolio(5,logic,self.df)
            self.assertAlmostEqual(expected,actual['summary']['objective'])

    def test_gp_exhaustive_zero_risk_target(self):
        targets={'potential':20.,'risk':0.,'strategic':150.}
        scales={'potential':20.,'risk':160.,'strategic':150.}
        weights={'potential':.2,'risk':.6,'strategic':.2}
        for logic in ['baseline','assumed_logic']:
            def penalty(x):
                return .2*max(0,20-self.df.investment_potential_score@x)/20 + .6*(self.df.risk_score@x)/160 + .2*max(0,150-self.df.strategic_score@x)/150
            expected=min(penalty(x) for x in self.feasible(logic))
            result=solve_goal_portfolio(self.df,5,targets,scales,weights,logic)
            self.assertAlmostEqual(expected,result['summary']['objective'],places=7)
            corrupt=copy.deepcopy(result)
            corrupt['summary']['d_risk_plus']=-1
            self.assertFalse(all(c['passed'] for c in validate(self.df,corrupt)))

    def test_validator_rejects_fractional_and_false_objective(self):
        result=solve_portfolio(5,df=self.df)
        corrupt=copy.deepcopy(result)
        corrupt['decisions'].loc[0,'x']=.5
        checks={r['check']:r['passed'] for r in validate(self.df,corrupt)}
        self.assertFalse(checks['binary'])
        corrupt=copy.deepcopy(result); corrupt['summary']['objective']+=1
        self.assertFalse(all(c['passed'] for c in validate(self.df,corrupt)))

    def test_empty_portfolio_and_invalid_budget(self):
        result=solve_portfolio(.5,df=self.df)
        self.assertEqual(result['summary']['projects_selected'],0)
        self.assertTrue(all(c['passed'] for c in validate(self.df,result)))
        with self.assertRaises(ValueError):
            solve_portfolio(-1,df=self.df)

    def test_scores_do_not_use_outcomes_or_ips(self):
        df=load_data(True); altered=df.copy()
        altered['status']='ipo'; altered['acquisition']=1; altered['ipo']=1
        altered['investment_potential_score']=0
        pd.testing.assert_series_equal(funding_history_risk(df),funding_history_risk(altered))
        pd.testing.assert_series_equal(strategic_alignment(df,config()['strategy']),strategic_alignment(altered,config()['strategy']))

    def test_invalid_score_inputs_fail(self):
        df=load_data(True); df['funding_rounds']=1
        with self.assertRaises(ValueError):
            funding_history_risk(df)
        df['sector']='unmapped'
        with self.assertRaises(ValueError):
            strategic_alignment(df,config()['strategy'])


if __name__=='__main__':
    unittest.main()
