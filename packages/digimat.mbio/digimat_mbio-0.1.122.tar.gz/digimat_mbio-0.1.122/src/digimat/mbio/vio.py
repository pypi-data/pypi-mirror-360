from .task import MBIOTask
from .xmlconfig import XMLConfig

import math


class MBIOTaskVirtualIO(MBIOTask):
    def initName(self):
        return 'vio'

    def onInit(self):
        pass

    def compileExpression(self, expression):
        try:
            code=compile(expression, '<string>', 'eval')
            if not code:
                self.logger.error('Unable to compile expression [%s]' % expression)

            variables={}
            for name in code.co_names:
                variables[name]=None

            return (code, variables)
        except:
            pass

    def evalExpression(self, code, variables={}):
        try:
            if code:
                r=eval(code, None, variables)
                return r
        except:
            pass
        return None

    def onLoad(self, xml: XMLConfig):
        items=xml.children('digital')
        if items:
            for item in items:
                name=item.get('name')
                if name:
                    self.valueDigital(name, default=item.getBool('default'), writable=True)

        items=xml.children('analog')
        if items:
            for item in items:
                name=item.get('name')
                unit=item.get('unit')
                resolution=item.getFloat('resolution', 0.1)
                if name:
                    self.value(name, unit=unit, default=item.getFloat('default'), writable=True, resolution=resolution)

        items=xml.children('variable')
        if items:
            for item in items:
                name=item.get('name')
                unit=item.get('unit')
                resolution=item.getFloat('resolution', 0.1)
                if name:
                    value=self.value(name, unit=unit, default=item.getFloat('default'), resolution=resolution)
                    value.config.set('x0', 0.0)
                    value.config.xmlUpdateFloat(item, 'x0', vmin=0)
                    value.config.set('x1', 100.0)
                    value.config.xmlUpdateFloat(item, 'x1', vmin=value.config.x0)
                    value.config.set('y0', 0.0)
                    value.config.xmlUpdateFloat(item, 'y0')
                    value.config.set('y1', 100.0)
                    value.config.xmlUpdateFloat(item, 'y1', vmin=value.config.y0)
                    expression=item.get('expression')
                    if expression:
                        value.config.set('expression', expression)
                        code, variables=self.compileExpression(expression)
                        value.config.set('code', code)
                        value.config.set('variables', variables)

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def eval(self, value):
        if value is not None:
            code=value.config.code
            if code is not None:
                variables=value.config.variables
                if variables:
                    mbio=self.getMBIO()
                    for name in variables.keys():
                        try:
                            variables[name]=mbio.value(name).value
                        except:
                            pass

                # self.logger.warning('%s <- %s' % (value, variables))

                v=None
                r=self.evalExpression(code, variables)
                if r is not None:
                    value.setError(False)
                    v=r

                try:
                    dy=(value.config.y1-value.config.y0)
                    dx=(value.config.x1-value.config.x0)
                    v=value.config.y0+(v-value.config.x0)/dx*dy
                    if v<value.config.y0:
                        v=value.config.y0
                    if v>value.config.y1:
                        v=value.config.y1
                except:
                    pass

                value.updateValue(v)
            else:
                value.setError(True)

    def run(self):
        for value in self.values:
            self.microsleep()

            if value.config.expression:
                self.eval(value)

            if value.isWritable() and value.isPendingSync():
                value.clearSyncAndUpdateValue()
        return 1.0


if __name__ == "__main__":
    pass
