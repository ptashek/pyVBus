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

DST="<destination path>"
RRD="<source rrd path>"
GRAPH_PREFIX=solar
GRAPH_SUFFIX=.png
FONT="/usr/share/fonts/dejavu/DejaVuSansMono.ttf"

case "$1" in
	"hour")
		SUBTITLE="(last 6h)"
		STARTAT="end-6h"
		;;

	"day")
		SUBTITLE="(last 24h)"
		STARTAT="end-24h"
		;;

	"week")
		SUBTITLE="(last 7d)"
		STARTAT="end-168h"
		;;
	*)
		echo "Unknown chart period" > /dev/stderr
		exit 1
		;;
esac

DSTFILE=${DST}/${GRAPH_PREFIX}_${1}${GRAPH_SUFFIX}
rrdtool graph ${DSTFILE} \
	--lazy \
	--start ${STARTAT} \
	--end now \
	-h 240 -w 720 \
	--title "Solar collector and buffer temps ${SUBTITLE}" \
	--vertical-label "*C / %" \
	-u 130 -l -10 --rigid \
	--slope-mode \
	--font TITLE:10:${FONT} \
	--font AXIS:6.5:${FONT} \
	--font LEGEND:7.5:${FONT} \
	--font UNIT:7.5:${FONT} \
	--font WATERMARK:6:${FONT} \
	--watermark "Last update: $(date)" \
	TEXTALIGN:left \
	DEF:collector=${RRD}:TS1:AVERAGE \
	DEF:buffer_bottom=${RRD}:TS2:AVERAGE \
	DEF:buffer_top=${RRD}:TS3:AVERAGE \
	DEF:pump_speed=${RRD}:R1S:AVERAGE \
	DEF:pump_hours=${RRD}:R1H:MAX \
	AREA:collector#D40D1250:"Collector [°C]		" \
	GPRINT:collector:LAST:"last\: %3.1lf %s"  \
	GPRINT:collector:AVERAGE:"avg\: %3.1lf %s"  \
	GPRINT:collector:MAX:"max\: %3.1lf%s"  \
	GPRINT:collector:MIN:"min\: %3.1lf %s\n"  \
	LINE2:buffer_bottom#55CF5FFF:"Buffer\: Ts, bottom [°C]	" \
	GPRINT:buffer_bottom:LAST:"last\: %3.1lf %s"  \
	GPRINT:buffer_bottom:AVERAGE:"avg\: %3.1lf %s"  \
	GPRINT:buffer_bottom:MAX:"max\: %3.1lf %s"  \
	GPRINT:buffer_bottom:MIN:"min\: %3.1lf %s\n"  \
	LINE2:buffer_top#FFA32EFF:"Buffer\: Tg, top [°C]	" \
	GPRINT:buffer_top:LAST:"last\: %3.1lf %s"  \
	GPRINT:buffer_top:AVERAGE:"avg\: %3.1lf %s"  \
	GPRINT:buffer_top:MAX:"max\: %3.1lf %s"  \
	GPRINT:buffer_top:MIN:"min\: %3.1lf %s\n"  \
	LINE2:pump_speed#0000FF50:"Pump speed [%]		" \
	GPRINT:pump_speed:LAST:"last\: %3.1lf %s" \
	GPRINT:pump_speed:AVERAGE:" avg\: %3.1lf %s\n" \
	LINE2:pump_hours#00000000:"Pump runtime		" \
	GPRINT:pump_hours:LAST:"%4.0lf hours\n" \
	TICK:pump_speed#00FF00:0.0175

# Optional x-axis grid configs
#		--x-grid MINUTE:5:HOUR:1:MINUTE:10:0:%R \
#		--x-grid MINUTE:10:HOUR:1:MINUTE:120:0:%R \
#		--x-grid MINUTE:360:HOUR:6:MINUTE:1440:0:"%d/%m\n %H:%M" \
