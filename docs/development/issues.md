Analyzing python code at: /home/sam/Projects/cross-section

Running mypy... found 176 issue(s)
Running ruff... found 253 issue(s)
Running radon... found 199 issue(s)
Running semgrep... ✓
Running vulture... found 1 issue(s)

Cache: 0 hits, 5 misses

╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Static Analysis Report - PYTHON                                                                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
        Summary        
 Total Issues    629   
   Errors        358   
   Warnings      21    
 Tools Run       5     
 Execution Time  5.36s 


Errors (358):
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:134:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:144:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:152:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:155:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:183:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:187:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:206:101 - [E501] Line too long (120 > 100)
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:221:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:223:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:224:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:225:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:226:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/basic_section.py:40:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/basic_section.py:50:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/basic_section.py:57:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:90:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:100:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:108:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:111:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:128:101 - [E501] Line too long (104 > 100)
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:134:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:152:101 - [E501] Line too long (104 > 100)
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:169:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:171:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:172:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:173:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:174:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:175:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:176:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/curb_and_gutter.py:177:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:125:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:135:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:143:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:146:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:156:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:167:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:178:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:210:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:212:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:213:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:214:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:215:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:216:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:217:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:218:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/cut_and_fill.py:219:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/layered_pavement.py:94:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/layered_pavement.py:104:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/layered_pavement.py:112:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/layered_pavement.py:115:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/layered_pavement.py:130:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/layered_pavement.py:157:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:102:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:112:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:120:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:123:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:137:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:145:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:160:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:178:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:180:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:181:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:182:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:183:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:144:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:154:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:162:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:165:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:193:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:197:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:226:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:241:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:243:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:244:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:245:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:246:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/roadside_ditch.py:247:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:131:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:141:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:149:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:152:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:162:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:170:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:180:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:191:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:199:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:220:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:222:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:223:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:224:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:225:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:226:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:227:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:228:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:229:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/shoring_example.py:230:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:119:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:129:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:137:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:140:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:155:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:165:101 - [E501] Line too long (121 > 100)
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:167:101 - [E501] Line too long (124 > 100)
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:170:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:186:19 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:195:101 - [E501] Line too long (121 > 100)
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:197:101 - [E501] Line too long (124 > 100)
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:211:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:213:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:214:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:215:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:216:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:217:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:218:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:219:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/symmetric_section.py:57:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/symmetric_section.py:67:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/symmetric_section.py:76:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/symmetric_section.py:79:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/symmetric_section.py:90:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/examples/symmetric_section.py:101:11 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/curbs.py:240:101 - [E501] Line too long (105 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/curbs.py:251:101 - [E501] Line too long (115 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/curbs.py:256:101 - [E501] Line too long (109 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py:6:24 - [F401] `..pavement.CrushedRockLayer` imported but unused
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py:6:42 - [F401] `..pavement.ConcreteLayer` imported but unused
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py:267:101 - [E501] Line too long (106 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py:339:101 - [E501] Line too long (106 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py:404:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py:409:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/lanes.py:186:101 - [E501] Line too long (109 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/lanes.py:188:101 - [E501] Line too long (114 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/lanes.py:202:101 - [E501] Line too long (103 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/lanes.py:204:101 - [E501] Line too long (105 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoring.py:106:9 - [F841] Local variable `attachment` is assigned to but never used
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoring.py:114:101 - [E501] Line too long (103 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoring.py:121:101 - [E501] Line too long (103 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoring.py:185:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:239:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:240:101 - [E501] Line too long (102 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:319:101 - [E501] Line too long (106 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:320:101 - [E501] Line too long (110 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:321:101 - [E501] Line too long (116 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:322:101 - [E501] Line too long (103 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:327:101 - [E501] Line too long (103 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:328:101 - [E501] Line too long (116 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:329:101 - [E501] Line too long (110 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:330:101 - [E501] Line too long (106 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:400:101 - [E501] Line too long (109 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:402:101 - [E501] Line too long (114 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:406:101 - [E501] Line too long (102 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:408:101 - [E501] Line too long (103 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:425:101 - [E501] Line too long (121 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:427:101 - [E501] Line too long (123 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/slopes.py:150:101 - [E501] Line too long (119 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:31:101 - [E501] Line too long (110 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:33:101 - [E501] Line too long (115 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:38:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:41:101 - [E501] Line too long (102 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:71:101 - [E501] Line too long (102 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:73:101 - [E501] Line too long (104 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:76:101 - [E501] Line too long (118 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:78:101 - [E501] Line too long (116 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:84:101 - [E501] Line too long (120 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:113:101 - [E501] Line too long (106 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:115:101 - [E501] Line too long (108 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:120:101 - [E501] Line too long (112 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/section.py:157:101 - [E501] Line too long (117 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/section.py:166:101 - [E501] Line too long (118 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/core/domain/section.py:216:101 - [E501] Line too long (134 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/export/svg.py:65:22 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/src/cross_section/export/svg.py:121:30 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/src/cross_section/export/svg.py:143:22 - [F541] f-string without any placeholders
  ✗ /home/sam/Projects/cross-section/src/cross_section/export/svg.py:158:101 - [E501] Line too long (101 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/export/svg.py:159:101 - [E501] Line too long (105 > 100)
  ✗ /home/sam/Projects/cross-section/src/cross_section/export/svg.py:185:101 - [E501] Line too long (103 > 100)
  ✗ /home/sam/Projects/cross-section/tests/core/test_layered_lane.py:80:101 - [E501] Line too long (107 > 100)
  ✗ /home/sam/Projects/cross-section/tests/core/test_layered_lane.py:81:101 - [E501] Line too long (112 > 100)
  ✗ /home/sam/Projects/cross-section/tests/core/test_pavement.py:3:8 - [F401] `pytest` imported but unused
  ✗ /home/sam/Projects/cross-section/tests/core/test_primitives.py:3:8 - [F401] `pytest` imported but unused
  ✗ /home/sam/Projects/cross-section/tests/core/test_primitives.py:4:8 - [F401] `math` imported but unused
  ✗ /home/sam/Projects/cross-section/tests/core/test_primitives.py:5:101 - [E501] Line too long (103 > 100)
  ✗ examples/asymmetric_cut_fill.py:11:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/asymmetric_cut_fill.py:80:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/asymmetric_cut_fill.py:88:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/asymmetric_cut_fill.py:113:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/asymmetric_cut_fill.py:121:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/asymmetric_cut_fill.py:183:38 - [arg-type] Argument 1 to "abs" has incompatible type "Any | None"; expected "SupportsAbs[Any]"
  ✗ examples/asymmetric_cut_fill.py:183:69 - [operator] Unsupported operand types for > ("int" and "None")
  ✗ examples/basic_section.py:7:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/basic_section.py:24:32 - [call-arg] Unexpected keyword argument "surface_type" for "TravelLane"
  ✗ examples/basic_section.py:31:32 - [call-arg] Unexpected keyword argument "surface_type" for "TravelLane"
  ✗ examples/curb_and_gutter.py:11:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/curb_and_gutter.py:73:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/curb_and_gutter.py:83:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/curb_and_gutter.py:127:40 - [operator] Unsupported operand types for * ("None" and "float")
  ✗ examples/curb_and_gutter.py:128:44 - [operator] Unsupported operand types for * ("None" and "float")
  ✗ examples/curb_and_gutter.py:129:39 - [operator] Unsupported operand types for * ("None" and "float")
  ✗ examples/curb_and_gutter.py:130:38 - [operator] Unsupported operand types for * ("None" and "float")
  ✗ examples/cut_and_fill.py:16:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/cut_and_fill.py:71:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/cut_and_fill.py:79:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[CrushedRockLayer]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/cut_and_fill.py:94:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/cut_and_fill.py:102:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[CrushedRockLayer]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/cut_and_fill.py:163:38 - [arg-type] Argument 1 to "abs" has incompatible type "Any | None"; expected "SupportsAbs[Any]"
  ✗ examples/layered_pavement.py:11:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/layered_pavement.py:57:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/layered_pavement.py:65:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/layered_pavement.py:89:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/road_with_shoulders.py:11:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/road_with_shoulders.py:73:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/road_with_shoulders.py:81:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/road_with_shoulders.py:89:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/road_with_shoulders.py:97:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/roadside_ditch.py:11:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/roadside_ditch.py:73:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/roadside_ditch.py:80:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/roadside_ditch.py:111:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/roadside_ditch.py:118:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/roadside_ditch.py:193:38 - [arg-type] Argument 1 to "abs" has incompatible type "Any | None"; expected "SupportsAbs[Any]"
  ✗ examples/roadside_ditch.py:193:69 - [operator] Unsupported operand types for > ("int" and "None")
  ✗ examples/shoring_example.py:17:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/shoring_example.py:72:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/shoring_example.py:80:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[CrushedRockLayer]"; expected "list[AsphaltLayer | ConcreteLayer 
| CrushedRockLayer]"
  ✗ examples/shoring_example.py:103:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/shoring_example.py:111:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[CrushedRockLayer]"; expected "list[AsphaltLayer | ConcreteLayer
| CrushedRockLayer]"
  ✗ examples/shoring_example.py:167:51 - [operator] Unsupported operand types for * ("None" and "float")
  ✗ examples/shoring_example.py:168:57 - [operator] Unsupported operand types for * ("None" and "float")
  ✗ examples/shoring_example.py:176:38 - [arg-type] Argument 1 to "abs" has incompatible type "Any | None"; expected "SupportsAbs[Any]"
  ✗ examples/slumped_shoulder.py:11:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/slumped_shoulder.py:88:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/slumped_shoulder.py:97:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/slumped_shoulder.py:105:24 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/slumped_shoulder.py:114:24 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ examples/symmetric_section.py:7:0 - [no-untyped-def] Function is missing a return type annotation
  ✗ examples/symmetric_section.py:25:31 - [call-arg] Unexpected keyword argument "surface_type" for "TravelLane"
  ✗ examples/symmetric_section.py:32:31 - [call-arg] Unexpected keyword argument "surface_type" for "TravelLane"
  ✗ examples/symmetric_section.py:41:32 - [call-arg] Unexpected keyword argument "surface_type" for "TravelLane"
  ✗ examples/symmetric_section.py:48:32 - [call-arg] Unexpected keyword argument "surface_type" for "TravelLane"
  ✗ src/cross_section/core/domain/components/curbs.py:34:30 - [assignment] Incompatible types in assignment (expression has type "None", variable has type "ConcreteLayer")
  ✗ src/cross_section/core/domain/components/curbs.py:36:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ src/cross_section/core/domain/components/ditches.py:43:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ src/cross_section/core/domain/components/shoulders.py:290:8 - [assignment] Incompatible types in assignment (expression has type "CrushedRockLayer", variable has type 
"AsphaltLayer")
  ✗ src/cross_section/core/domain/components/slopes.py:31:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ src/cross_section/core/domain/components/slopes.py:76:23 - [operator] Unsupported operand types for - ("float" and "None")
  ✗ src/cross_section/core/domain/components/slopes.py:80:18 - [operator] Unsupported operand types for + ("float" and "None")
  ✗ src/cross_section/core/domain/components/slopes.py:86:18 - [operator] Unsupported operand types for - ("float" and "None")
  ✗ src/cross_section/core/domain/components/slopes.py:150:73 - [operator] Unsupported operand types for / ("None" and "float")
  ✗ src/cross_section/core/domain/components/slopes.py:150:99 - [arg-type] Argument 1 to "abs" has incompatible type "float | None"; expected "SupportsAbs[float]"
  ✗ src/cross_section/core/domain/components/slopes.py:165:11 - [operator] Unsupported operand types for >= ("int" and "None")
  ✗ src/cross_section/core/domain/components/slopes.py:168:15 - [arg-type] Argument 1 to "abs" has incompatible type "float | None"; expected "SupportsAbs[float]"
  ✗ src/cross_section/core/domain/components/slopes.py:172:23 - [operator] Unsupported operand types for / ("None" and "float")
  ✗ src/cross_section/core/domain/components/slopes.py:172:49 - [arg-type] Argument 1 to "abs" has incompatible type "float | None"; expected "SupportsAbs[float]"
  ✗ tests/core/test_components.py:11:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:21:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:37:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:46:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:55:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:69:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:83:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:101:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:119:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:135:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:142:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:149:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_components.py:156:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_layered_lane.py:15:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_layered_lane.py:23:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_layered_lane.py:31:53 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_layered_lane.py:37:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_layered_lane.py:47:53 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_layered_lane.py:60:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_layered_lane.py:68:53 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_layered_lane.py:91:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_layered_lane.py:99:53 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[AsphaltLayer]"; expected "list[AsphaltLayer | 
ConcreteLayer | CrushedRockLayer]"
  ✗ tests/core/test_layered_lane.py:106:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_layered_lane.py:131:73 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_layered_lane.py:132:74 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_layered_lane.py:133:74 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_pavement.py:10:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:25:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:37:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:50:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:67:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:80:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:90:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:102:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:118:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:131:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_pavement.py:141:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:11:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:17:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:23:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:33:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:43:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:55:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:67:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:73:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:85:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:96:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:110:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:117:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:126:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:133:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_primitives.py:143:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:11:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:18:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:31:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:37:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:47:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:57:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:71:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:85:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:96:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:105:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:120:74 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[AsphaltLayer]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_section.py:121:74 - [arg-type] Argument "pavement_layers" to "TravelLane" has incompatible type "list[AsphaltLayer]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_section.py:126:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:137:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:151:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:175:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_section.py:195:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:11:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:18:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:29:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:38:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:47:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:60:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:73:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:86:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:99:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:134:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:166:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:198:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:230:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:236:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:242:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:249:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:256:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:263:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:270:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:277:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:284:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:291:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoring.py:298:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:11:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:20:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:33:28 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_shoulder.py:41:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:50:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:64:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:77:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:90:28 - [arg-type] Argument "pavement_layers" to "Shoulder" has incompatible type "list[object]"; expected "list[AsphaltLayer | ConcreteLayer | 
CrushedRockLayer]"
  ✗ tests/core/test_shoulder.py:120:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:146:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:161:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:168:4 - [no-untyped-def] Function is missing a return type annotation
  ✗ tests/core/test_shoulder.py:175:4 - [no-untyped-def] Function is missing a return type annotation

Warnings (21):
  ⚠ /home/sam/Projects/cross-section/examples/asymmetric_cut_fill.py:11:0 - [C15] function 'main' has complexity 15 (rank C)
  ⚠ /home/sam/Projects/cross-section/examples/cut_and_fill.py:16:0 - [C13] function 'main' has complexity 13 (rank C)
  ⚠ /home/sam/Projects/cross-section/examples/road_with_shoulders.py:11:0 - [C13] function 'main' has complexity 13 (rank C)
  ⚠ /home/sam/Projects/cross-section/examples/roadside_ditch.py:11:0 - [C17] function 'main' has complexity 17 (rank C)
  ⚠ /home/sam/Projects/cross-section/examples/shoring_example.py:17:0 - [C15] function 'main' has complexity 15 (rank C)
  ⚠ /home/sam/Projects/cross-section/examples/slumped_shoulder.py:11:0 - [C15] function 'main' has complexity 15 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/curbs.py:223:4 - [C15] method 'validate' has complexity 15 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py:388:4 - [C13] method 'validate' has complexity 13 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/lanes.py:168:4 - [C12] method 'validate' has complexity 12 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py:382:4 - [C16] method 'validate' has complexity 16 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:8:0 - [C11] class 'AsphaltLayer' has complexity 11 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:50:0 - [C15] class 'ConcreteLayer' has complexity 15 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py:64:4 - [C14] method 'validate' has complexity 14 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/domain/section.py:120:4 - [C11] method 'validate' has complexity 11 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/geometry/primitives.py:88:0 - [C16] class 'ComponentGeometry' has complexity 16 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/core/geometry/primitives.py:95:4 - [C15] method 'bounds' has complexity 15 (rank C)
  ⚠ /home/sam/Projects/cross-section/src/cross_section/export/svg.py:32:4 - [C11] method 'export' has complexity 11 (rank C)
  ⚠ /home/sam/Projects/cross-section/tests/core/test_shoring.py:99:4 - [C17] method 'test_to_geometry_fill_right' has complexity 17 (rank C)
  ⚠ /home/sam/Projects/cross-section/tests/core/test_shoring.py:134:4 - [C14] method 'test_to_geometry_fill_left' has complexity 14 (rank C)
  ⚠ /home/sam/Projects/cross-section/tests/core/test_shoring.py:166:4 - [C14] method 'test_to_geometry_cut_right' has complexity 14 (rank C)
  ⚠ /home/sam/Projects/cross-section/tests/core/test_shoring.py:198:4 - [C14] method 'test_to_geometry_cut_left' has complexity 14 (rank C)

Analysis completed with 358 error(s).
