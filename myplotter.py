from backtrader_plotly.plotter import BacktraderPlotly
import backtrader as bt
import plotly.graph_objects as go
import numpy as np

class MyPlottly(BacktraderPlotly):
    def plotdata(self, data, indicators):
        for ind in indicators:
            upinds = self.dplotsup[ind]
            for upind in upinds:
                self.plotind(data, upind,
                             subinds=self.dplotsover[upind],
                             upinds=self.dplotsup[upind],
                             downinds=self.dplotsdown[upind])

        opens = data.open.plotrange(self.pinf.xstart, self.pinf.xend)
        highs = data.high.plotrange(self.pinf.xstart, self.pinf.xend)
        lows = data.low.plotrange(self.pinf.xstart, self.pinf.xend)
        closes = data.close.plotrange(self.pinf.xstart, self.pinf.xend)
        volumes = data.volume.plotrange(self.pinf.xstart, self.pinf.xend)
        datetime = data.datetime.plotrange(self.pinf.xstart, self.pinf.xend)

        vollabel = 'Volume'
        pmaster = data.plotinfo.plotmaster
        if pmaster is data:
            pmaster = None

        datalabel = ''
        if hasattr(data, '_name') and data._name:
            datalabel += data._name

        voloverlay = (self.pinf.sch.voloverlay and pmaster is None)

        if not voloverlay:
            vollabel += ' ({})'.format(datalabel)

        # if self.pinf.sch.volume and self.pinf.sch.voloverlay:
        axdatamaster = None
        if self.pinf.sch.volume and voloverlay:
            volplot = self.plotvolume(data, opens, highs, lows, closes, volumes, vollabel)
            axvol = self.pinf.daxis[data.volume]
            ax = axvol
            self.pinf.daxis[data] = ax
            self.pinf.vaxis.append(ax)
        else:
            if pmaster is None:
                ax = self.newaxis(data, rowspan=self.pinf.sch.rowsmajor)
            elif getattr(data.plotinfo, 'sameaxis', False):
                axdatamaster = self.pinf.daxis[pmaster]
                ax = axdatamaster
            else:
                axdatamaster = self.pinf.daxis[pmaster]
                ax = axdatamaster
                self.pinf.vaxis.append(ax)

        if hasattr(data, '_compression') and hasattr(data, '_timeframe'):
            tfname = bt.TimeFrame.getname(data._timeframe, data._compression)
            datalabel += ' (%d %s)' % (data._compression, tfname)

        plinevalues = getattr(data.plotinfo, 'plotlinevalues', True)

        # Get x axis data
        xdata = datetime or self.pinf.xreal
        xdata = [bt.num2date(x) for x in xdata]
        if self.pinf.sch.style.startswith('line'):
            if self.pinf.sch.linevalues and plinevalues:
                datalabel += f' C:{closes[-1]:.{self.pinf.sch.decimal_places}f}'

            if axdatamaster is None:
                color = self.pinf.sch.loc
            else:
                self.pinf.nextcolor(axdatamaster)
                color = self.pinf.color(axdatamaster)

            self.fig.add_trace(go.Scatter(x=np.array(xdata),
                                          y=np.array(closes),
                                          name=self.wrap_legend_text(datalabel),
                                          ), row=ax, col=1, secondary_y=True
                               )
            # self.fig['layout'][f'xaxis{ax}']['type'] = 'category'
            self.fig['layout'][f'yaxis{2 * ax}']['tickformat'] = f'.{self.pinf.sch.decimal_places}f'

        else:
            if self.pinf.sch.linevalues and plinevalues:
                datalabel += (f' O:{opens[-1]:.{self.pinf.sch.decimal_places}f} '
                              f'H:{highs[-1]:.{self.pinf.sch.decimal_places}f} '
                              f'L:{lows[-1]:.{self.pinf.sch.decimal_places}f} '
                              f'C:{closes[-1]:.{self.pinf.sch.decimal_places}f}'
                              )
            if self.pinf.sch.style.startswith('candle'):
                self.fig.add_trace(go.Candlestick(x=np.array(xdata),
                                                  open=np.array(opens),
                                                  high=np.array(highs),
                                                  low=np.array(lows),
                                                  close=np.array(closes),
                                                  increasing_line_color=self.pinf.sch.barup,
                                                  decreasing_line_color=self.pinf.sch.bardown,
                                                  name=self.wrap_legend_text(datalabel),
                                                  ), row=ax, col=1, secondary_y=True
                                   )
                # self.fig['layout'][f'xaxis{ax}']['type'] = 'category'
                self.fig['layout'][f'xaxis{ax}']['rangeslider']['visible'] = False
                self.fig['layout'][f'yaxis{2 * ax}']['tickformat'] = f'.{self.pinf.sch.decimal_places}f'
                self.fig.update_layout(hovermode='x unified')

        for ind in indicators:
            self.plotind(data, ind, subinds=self.dplotsover[ind], masterax=ax, secondary_y=True)

        a = axdatamaster or ax

        for ind in indicators:
            downinds = self.dplotsdown[ind]
            for downind in downinds:
                self.plotind(data, downind,
                             subinds=self.dplotsover[downind],
                             upinds=self.dplotsup[downind],
                             downinds=self.dplotsdown[downind],
                             )

        self.pinf.legpos[a] = len(self.pinf.handles[a])
