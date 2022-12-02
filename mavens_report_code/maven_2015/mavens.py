import pandas as pd

def extract():
    df_details = pd.read_csv('order_details.csv')
    df_orders = pd.read_csv('orders.csv')
    df_orders["date"] = pd.to_datetime(df_orders["date"], format='%d/%m/%Y') 
    df_types = pd.read_csv('pizza_types.csv',sep=';')

    return df_details, df_orders, df_types

def transform(df_details, df_orders, df_types):

    month = []
    day = []
    day_sem = []
    sem = []
    semana = 1
    date = df_orders["date"]
    for d in date:
        d = str(d)
        d = d.split('-')
        day.append(int(d[2].split(' ')[0]))
        month.append(int(d[1]))
        day_sem.append((int(d[2].split(' ')[0])+2)%7+1)
        if (int(d[2].split(' ')[0])+2)%7+1 == 1 and day_sem[-1] != day_sem[-2]:
            semana +=  1
        sem.append(semana)

    details = list(df_details.loc[:,'order_id'])
    month_1 = []
    day_1 = []
    day_sem_1 = []
    sem_1 = []
    for i in details:
        month_1.append(month[i-1])
        day_1.append(day[i-1])
        day_sem_1.append(day_sem[i-1])
        sem_1.append(sem[i-1])

    df_details.insert(3,'month',month_1)
    df_details.insert(4,'sem',sem_1)
    df_details.insert(5,'day',day_1)

    variables = ['quantity']
    columnas = ['pizza_id','month','sem'] + variables
    df_selec = df_details.loc[:, columnas] 

    QUANT = list(df_selec['quantity'])
    suma = 0
    p = []
    pizzas = []
    for i in range(1,len(QUANT)):
        suma += QUANT[i]
    for j in range(1,46):
        p = []
        for i in range(len(df_selec)):
            if df_selec['sem'][i] == j:
                for k in range(int(df_selec['quantity'][i])):
                    p.append(df_selec['pizza_id'][i])
        s = 0
        m = 0
        l = 0
        sm = []
        mm = []
        lm = []
        for tam in p:
            if tam.split('_')[-1] == 'm':
                m += 1
                pal = ''
                for el in tam.split('_')[:-1]:
                    pal += el + '_'
                mm.append(pal[:-1])
            elif tam.split('_')[-1] == 'l':
                l +=1
                pal = ''
                for el in tam.split('_')[:-1]:
                    pal += el + '_'
                lm.append(pal[:-1])
            elif tam.split('_')[-1] == 's':
                s += 1
                pal = ''
                for el in tam.split('_')[:-1]:
                    pal += el + '_'
                sm.append(pal[:-1])
        pizzas.append(sm)
        pizzas.append(mm)
        pizzas.append(lm)

    total = []
    count = {}
    dict_p = {}
    for p in pizzas:
        count = {}
        claves = list(dict.fromkeys(p))
        for c in claves:
            count[c] = p.count(c)
        total.append(count)
    for d in df_types['pizza_type_id;name;category;ingredients']:
        d = d.split(';')
        d[-1] = d[-1][:-1]
        d[3] = d[3][1:]
        j = 0
        while j < len(d):
            if d[j][0]==' ':
                d[j] = d[j][1:]
            j+=1
        dict_p[d[0]]=d[3:]
    
    def comprobar(ing,dic):
        for i in dic:
            if i == ing:
                return True
        return False

    def comprobar_s(dic):
        for i in dic:
            if i.split(' ') == 'Sauce':
                return False
        return True

    j = 0
    i_sem_total = []
    while j < len(total):
        i_sem = {}
        for c in list(total[j].keys()):
            valor = (j+1)%3
            if valor == 0:
                valor = 3
            valor = valor * int(total[j][c])
            existe = comprobar('Mozzarella Cheese',list(i_sem.keys()))
            if existe:
                i_sem['Mozzarella Cheese'] = i_sem['Mozzarella Cheese'] + valor
            else:
                    i_sem['Mozzarella Cheese'] = valor
            existe = comprobar('Tomato Sauce',list(i_sem.keys()))
            no_salsa = comprobar_s(list(i_sem.keys()))
            if existe and no_salsa:
                i_sem['Tomato Sauce'] = i_sem['Tomato Sauce'] + valor
            else:
                if no_salsa:
                    i_sem['Tomato Sauce'] = valor
            for ing in dict_p[c]:
                existe = comprobar(ing,list(i_sem.keys()))
                if existe:
                    i_sem[ing] = i_sem[ing] + valor
                else:
                    i_sem[ing] = valor
                    
        if j%3 == 0 and j != 0:
            i_sem_total.append(i_sem)    
        j += 1
        
    def menu(df_details,i_sem_total):
        print('Introduzca una fecha en el siguiente formato : dd-mm')
        c  = input()
        c = c.split('-')
        c[0] = int(c[0])
        c[1]=int(c[1])
        ind_filas = (df_details.day == c[0]) & (df_details.month == c[1])
        h = df_details.loc[ind_filas]['sem'].array[0]
        
        return i_sem_total[h-1]

    c = menu(df_details,i_sem_total)
    
    return c

def load(c):
    print(c)

if __name__=="__main__":
    df_details, df_orders, df_types = extract()
    c = transform(df_details, df_orders, df_types)
    load(c)