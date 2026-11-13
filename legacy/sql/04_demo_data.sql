-- All records below are SYNTHETIC DEMONSTRATION DATA, not historical market data.
INSERT INTO companies VALUES
(1,'NVIDIA','NVDA','Technology'),(2,'AMD','AMD','Technology'),
(3,'Microsoft','MSFT','Technology'),(4,'JPMorgan Chase','JPM','Finance'),
(5,'Exxon Mobil','XOM','Energy');
INSERT INTO models VALUES
(1,'Demo Reasoning Model','v1'),(2,'Rule-based Demo Model','v1');
INSERT INTO news VALUES
(1,'AI-chip demand rises','Demand for AI accelerators increases alongside new data-center investment.','2026-08-01','Demo / simulated'),
(2,'Cloud infrastructure spending expands','Cloud providers announce plans to expand AI infrastructure capacity.','2026-08-05','Demo / simulated'),
(3,'Bank lending expectations improve','A fictional report signals improving demand for business lending.','2026-08-10','Demo / simulated'),
(4,'Energy prices face supply pressure','A hypothetical supply disruption may increase energy prices.','2026-08-12','Demo / simulated'),
(5,'Chip supply competition intensifies','Fictional market commentary anticipates intense semiconductor competition.','2026-08-15','Demo / simulated'),
(6,'Enterprise AI adoption increases','More enterprises are hypothetically expanding AI software budgets.','2026-08-18','Demo / simulated');
INSERT INTO investments VALUES
(1,1,1,10000,'BUY','2026-08-02',8.0),
(2,2,1,8000,'BUY','2026-08-06',5.0),
(3,3,1,9000,'BUY','2026-08-19',3.0),
(4,4,2,7000,'BUY','2026-08-11',2.5),
(5,5,2,6000,'BUY','2026-08-13',-1.5),
(6,2,1,11000,'BUY','2026-08-16',-2.0),
(7,1,1,12000,'BUY','2026-08-07',4.0),
(8,4,2,5000,'BUY','2026-08-12',1.0);
INSERT INTO investment_reasoning VALUES
(1,1,1,'Rising AI data-center demand could support GPU revenue.',0.85,'memory_1'),
(2,2,2,'AI infrastructure expansion could benefit competing chip suppliers.',0.78,'memory_2'),
(3,3,6,'Enterprise AI adoption could support recurring cloud revenue.',0.74,'memory_3'),
(4,4,3,'Improving business lending demand could lift banking earnings.',0.68,'memory_4'),
(5,5,4,'Supply pressure might increase energy prices but volatility is high.',0.63,'memory_5'),
(6,6,5,'Chip competition could change margins despite strong demand.',0.58,'memory_6'),
(7,7,2,'More AI infrastructure spending could strengthen accelerator demand.',0.81,'memory_7'),
(8,8,3,'Better lending expectations might support banking profits.',0.67,'memory_8');
