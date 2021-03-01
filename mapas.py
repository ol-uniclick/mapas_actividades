import pandas as pd
import datetime
import numpy as np
from IPython.display import HTML
pd.options.mode.chained_assignment = None


TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

class Mapa():
    """Mapas de actividades.
    """

    def __init__(self, filename, delimiter=None):
        self.filename = filename
        self.df = self.load_csv(delimiter=delimiter)
        self.backup = self.load_csv(delimiter=delimiter)

    def load_csv(self, delimiter=None):
        """Carga el archivo csv.
        """
        data = pd.read_csv(self.filename, delimiter=delimiter,
                           dtype={'ID_OBJETIVO': str, 'ID_PRIMARIA': str,
                                  'ID_SECUNDARIA': str, 'ID_PUNTUAL': str,
                                  'SEMANA_INICIO': str, 'SEMANA_FIN': str})
        return data

    def fix_id(self):
        """Corrige los valores de los IDs para que sean número en string
        con dos dígitos.
        """
        data = self.df
        columnas = ['ID_OBJETIVO', 'ID_PRIMARIA',
                    'ID_SECUNDARIA', 'ID_PUNTUAL']
        for c in columnas:
            data = data.astype({c: str})
            for i in range(len(data[c])):
                data[c][i] = str(data[c][i]).zfill(2)
        self.df = data

    def fix_dtypes(self):
        """Corrige los datatypes para que todas las columnas sean de
        tipo str, a excepción de la columna SEMANA, la cual es int.
        """
        data = self.df
        data = data.astype(str)
        data = data.astype({'SEMANA': int})
        self.df = data

    def upper(self):
        """Convierte todo el texto a mayúsculas.
        """
        self.df = self.df.apply(lambda x: x.astype(str).str.upper())
        self.df.columns = map(str.upper, self.df.columns)

    def fix_format(self):
        """Convierte todo el texto a mayúsculas y elimina los acentos
        de todos los string.
        """
        self.upper()
        self.df = self.df.replace(regex=r'Á', value='A')
        self.df = self.df.replace(regex=r'É', value='E')
        self.df = self.df.replace(regex=r'Í', value='I')
        self.df = self.df.replace(regex=r'Ó', value='O')
        self.df = self.df.replace(regex=r'Ú', value='U')
        self.df = self.df.replace(regex=r'Ü', value='U')

    def update_week(self):
        """Actualiza la columna de SEMANA al número de semana actual.
        """
        self.df['SEMANA'] = datetime.datetime.now().isocalendar()[1] + 1

    def update_status(self):
        """Actualiza el estatus de las actividades de acuerdo a los
        valores de las columnas de las semanas.
        """
        data = self.df
        col_names = ['SEMANA_INICIO', 'SEMANA_FIN', 'SEMANA']
        dat = [np.array(data[col]) for col in col_names]

        new_status = [estatus_puntual(dat[0][i], dat[1][i], dat[2][i])
                      for i in range(len(dat[0]))]

        for i in range(len(new_status)):
            if data['ESTATUS_PUNTUAL'][i] not in ['TERMINADO', 'RECURRENTE']:
                data['ESTATUS_PUNTUAL'][i] = new_status[i]
        self.df = data

    def terminado(self, index_):
        """Pone el valor de la columna ESTATUS_PUNTUAL con renglón
        index_ como 'TERMINADO'.
        """
        index_ = int(index_)
        self.df['ESTATUS_PUNTUAL'][index_] = 'TERMINADO'

    def recurrente(self, index_):
        """Pone el valor de la columna ESTATUS_PUNTUAL con renglón
        index_ como 'RECURRENTE'.
        """
        index_ = int(index_)
        self.df['ESTATUS_PUNTUAL'][index_] = 'RECURRENTE'

    def semanas(self, index_):
        """Para regresar al valor de semanas que se calculó con el
        método update_status en el renglón index_.
        """
        index_ = int(index_)
        self.df['ESTATUS_PUNTUAL'][index_] = ''
        self.update_status()

    def set_status(self, status, index_):
        """Pone el valor de la columna ESTATUS_PUNTUAL con renglón
        index_ de acuerdo al valor que se pase en el argumentos status.
        En caso de que status='SEMANAS' regresa al valor de semanas que
        se calcula con el método update_status.
        """
        index_ = int(index_)
        status = status.strip().upper()
        if status == 'TERMINADO':
            self.terminado(index_)
        elif status == 'RECURRENTE':
            self.recurrente(index_)
        elif status == 'SEMANAS' or status == 'SEMANA':
            self.semanas(index_)
        else:
            print(u'Introduzca un valor de estatus válido:\n'
                +'TERMINADO/RECURRENTE/SEMANAS')

    def fix_all(self, update=True):
        """Aplica todas las correcciones y opcionalmente la actualización
        de semana en curso.
        """
        self.fix_format()
        self.fix_id()
        self.fix_dtypes()
        if update:
            self.update_week()
            self.update_status()

    def to_file(self, sep='|', path='', filename=f'mapa_{TIMESTAMP}.txt'):
        """Guarda el mapa en un archivo. Por default se guarda como un
        archivo txt etiquetado con una timestamp.
        """
        self.df.to_csv(path+filename, index=None, sep='|', quoting=2)

    def status(self, status):
        """Devuelve las filas cque cumplan el status seleccionado.
        """
        status = status.strip().upper()
        dic = {'TERMINADO': 'TERMINADO', 'RECURRENTE': 'RECURRENTE',
            'PENDIENTE': 'PENDIENTE', 'EN PROCESO': r'^\d', 'ATRASADO': r'^-'}
        if status in dic:
            out = self.df[self.df['ESTATUS_PUNTUAL'].str.match(dic[status])]
        else:
            print(u'Introduzca un valor de estatus válido:\n'
                +'TERMINADO/RECURRENTE/PENDIENTE/ATRASADO/EN PROCESO')
            out = None
        return out



#------------------------------------------------------------------------------
def estatus_puntual(ini, fin, actual):
    """Calcula el valor de las columnas de SEMANA_INICIO y SEMANA_FIN
    a partir de la semana en curso.
    """
    ini = int(ini)
    fin = int(fin)
    actual = int(actual)
    dif = ini - fin
    sem = 'SEMANAS'
    if actual < ini:
        estatus = 'PENDIENTE'
    elif actual <= fin and actual >= ini:
        dias = fin - actual + 1
        if dias == 1: sem = 'SEMANA'
        estatus = f'{dias} {sem}'
    elif actual > fin:
        dias = fin - actual
        if dias == -1: sem = 'SEMANA'
        estatus = f'{dias} {sem}'
    return estatus

def view(df):
    """Desplegar la tabla fuera del notebook.
    """
    css = """<style>
    table { border-collapse: collapse; border: 3px solid #eee; }
    table tr th:first-child { background-color: #eeeeee; color: #333; font-weight: bold }
    table thead th { background-color: #eee; color: #000; }
    tr, th, td { border: 1px solid #ccc; border-width: 1px 0 0 1px; border-collapse: collapse;
    padding: 3px; font-family: monospace; font-size: 10px }</style>
    """
    s  = '<script type="text/Javascript">'
    s += ('var win = window.open("", "Title", "toolbar=no, location=no, '
    + 'directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, '
    + 'width=780, height=200, top="+(screen.height-400)+", '
    + 'left="+(screen.width-840)); win.document.body.innerHTML = \''
    + (df.to_html() + css).replace("\n",'\\') + '\';')
    s += '</script>'
    return (HTML(s+css))

def inicio_semana(week, year):
    """
    """
    d = f'{year}-W{week-1}'
    r = datetime.datetime.strptime(d + '-1', '%G-W%V-%u')
    s = r.strftime('%d/%m/%Y')
    return s

def fin_semana(week, year):
    """
    """
    d = f'{year}-W{week-1}'
    r = datetime.datetime.strptime(d + '-5', '%G-W%V-%u')
    s = r.strftime('%d/%m/%Y')
    return s

def resumen_actividades(df, fecha_fin=False, filter_=[]):
    """
    """
    cols = ['LINEA', 'OBJETIVO', 'ACTIVIDAD_PRIMARIA',
            'ACTIVIDAD_SECUNDARIA', 'ACTIVIDAD_PUNTUAL']
    df = df.astype({'SEMANA_FIN': int})
    df = df.set_index(cols).sort_index().sort_values(by=['SEMANA_FIN'])

    for level0 in df.index.levels[0]:
        print(level0)
        for level1 in df.index.levels[1]:
            print('    '*1+level1)
            for level2 in df.index.levels[2]:
                print('    '*2+level2)
                for level3 in df.index.levels[3]:
                    print('    '*3+level3)
                    sub_df = df.xs([level0, level1, level2, level3])
                    sub_df = sub_df.astype({'SEMANA_FIN': int})
                    sub_df = sub_df.sort_values(by=['SEMANA_FIN'])
                    for n in list(sub_df.index):
                        imp = sub_df.loc[n, 'IMPORTANCIA_PUNTUAL']
                        if imp not in filter_:
                            semana = int(sub_df.loc[n, 'SEMANA_FIN'])
                            fin = ', '+fin_semana(semana, 2021)
                            #inicio = ', '+inicio_semana(semana, 2021)
                            if fecha_fin == False: fin = ''
                            print('    '*4+n+fin)
