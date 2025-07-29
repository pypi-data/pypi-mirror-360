#!/usr/bin/env python
#-*- coding: utf-8 -*-
# @file      : arrayops.py
# @author    : Zhi Liu
# @email     : zhiliu.mind@gmail.com
# @homepage  : http://iridescent.ink
# @date      : Sun Nov 27 2019
# @version   : 0.0
# @license   : The GNU General Public License (GPL) v3.0
# @note      : 
# 
# The GNU General Public License (GPL) v3.0
# Copyright (C) 2013- Zhi Liu
#
# This file is part of torchbox.
#
# torchbox is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software Foundation, 
# either version 3 of the License, or (at your option) any later version.
#
# torchbox is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with torchbox. 
# If not, see <https://www.gnu.org/licenses/>. 
#

import torch as th
import torchbox as tb

device = 'cuda:0'
th.manual_seed(2020)
Ns, k, b = 200, 1.5, 3.0
x = th.linspace(0, 10, Ns)
t = x * k + b
t = tb.awgn(t, snrv=30)

deg = (0, 1)

model = tb.PolyFit(deg=deg).to(device)

dstrain = th.utils.data.TensorDataset(x, t)
dltrain = th.utils.data.DataLoader(dstrain, batch_size=50, shuffle=True)
dsvalid = th.utils.data.TensorDataset(x, t)
dlvalid = th.utils.data.DataLoader(dsvalid, batch_size=20, shuffle=False)

criterions = [[tb.SSELoss(reduction='sum'), tb.SSELoss(reduction='sum')]]
criterionws = [[1., 0.5]]
optimizer = th.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-2)
scheduler = th.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.98)

for n in range(1000):
    losstrain = tb.train_epoch(model, dltrain, 1, criterions, criterionws=criterionws, optimizer=optimizer, scheduler=None, epoch=n, logf='stdout', device=device)
    lossvalid = tb.valid_epoch(model, dlvalid, 1, criterions, criterionws=criterionws, epoch=n, logf='stdout', device=device)
    scheduler.step()
    print(model.w[0].item(), model.w[1].item(), scheduler.get_lr())
y = tb.demo_epoch(model, x, 10, logf='stdout', device=device)

print(y.shape)
plt = tb.plot([[y.cpu(), t]], Xs=[[x, x]], legends=[['Pred', 'GT']])
plt.show()
