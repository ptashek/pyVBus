#!/bin/bash
# Copyright 2013 Lukasz Szmit
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

rrdtool create $1 --step 1 --start $(( date +%s )) \
	DS:TS1:GAUGE:300:U:200 \
	DS:TS2:GAUGE:300:U:200 \
	DS:TS3:GAUGE:300:U:200 \
	DS:TS4:GAUGE:300:U:200 \
	DS:R1S:GAUGE:300:0:100 \
	DS:R2S:GAUGE:300:0:100 \
	DS:R1H:ABSOLUTE:300:0:U \
	DS:R2H:ABSOLUTE:300:0:U \
	RRA:AVERAGE:0.5:60:1440 \
	RRA:AVERAGE:0.5:3600:744 \
	RRA:AVERAGE:0.5:86400:365 \
	RRA:MIN:0.5:60:1440 \
	RRA:MIN:0.5:3600:744 \
	RRA:MIN:0.5:86400:365 \
	RRA:MAX:0.5:60:1440 \
	RRA:MAX:0.5:3600:744 \
	RRA:MAX:0.5:86400:365 \
	RRA:LAST:0.5:60:1440 \
	RRA:LAST:0.5:3600:744 \
	RRA:LAST:0.5:86400:365
