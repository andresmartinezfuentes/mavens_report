import pandas as pd
import datetime
from copy import deepcopy
import xlsxwriter


def extract():
    df_details = pd.read_csv('unformatted_order_details.csv',sep=';')
    df_orders = pd.read_csv('unformatted_orders.csv',sep=';')
    df_orders = df_orders.drop(df_orders.loc[pd.isna(df_orders['date'])].index)
    df_pizzas = pd.read_csv('pizzas.csv')
    df_types = pd.read_csv('pizza_types.csv',sep=',')
    return df_types, df_pizzas, df_orders, df_details

def transform(df_types, df_pizzas, df_orders, df_details):
    lista = []
    for i in list(df_orders.index):
        try:
            c = float(df_orders.date[i])
            lista.append(datetime.datetime.fromtimestamp(c).strftime('%d/%m/%Y'))
        except:
            lista.append(df_orders["date"][i])
    df_orders["date"] = lista
    df_orders["date"] = pd.to_datetime(df_orders["date"])
    df_orders = df_orders.sort_values('order_id')
    df_details = df_details.drop(df_details.loc[pd.isna(df_details['quantity'])].index)
    df_details = df_details.drop(df_details.loc[pd.isna(df_details['pizza_id'])].index)
    pizza_id = []
    for el in df_details['pizza_id']:
        el = el.replace(' ','_')
        el = el.replace('-','_')
        el = el.replace('@','a')
        el = el.replace('0','o')
        el = el.replace('3','e')
        pizza_id.append(el)
    df_details['pizza_id'] = pizza_id
    df_details = df_details.sort_values('order_id')

    quant = []
    for el in df_details['quantity']:
        el = el.replace('One','1')
        el = el.replace('Two','2')
        el = el.replace('one','1')
        el = el.replace('two','2')
        quant.append(int(el))
    df_details['quantity'] = quant 
    c1 , c2 = list(set(df_orders['order_id'])) , list(set(df_details['order_id']))
    el_no = []
    for c in c1:
        for el in c2:
            if c == el:
                el_no.append(c)
    df_details = df_details.loc[df_details.order_id.isin(el_no)]
    df_orders = df_orders.loc[df_orders.order_id.isin(el_no)]
    def dia_sem(dia,mes,año):
        a = int((14 - mes) / 12)
        y = año - a
        m = int(mes + (12 * a) - 2)
        d = int(dia + y + int(y/4) - int(y/100) + int(y/400)+((31*m) / 12)) % 7
        if d == 0:
            d = 7
        return d

    l_emmjaod = [i for i in range(1,32)]
    l_ajsn = [i for i in range(1,31)]
    l_f = [i for i in range(1,29)]
    dict_sem = {}
    semana = 1
    for i in range(1,13):
        if i % 2 == 0:
            if i == 2:
                lista = l_f
            elif i >= 8:
                lista = l_emmjaod
            else:
                lista = l_ajsn
        else:
            if i >= 8:
                lista = l_ajsn
            else:
                lista = l_emmjaod
        for j in lista:
            dict_sem[str(j)+'-'+str(i)] = []
            dict_sem[str(j)+'-'+str(i)].append(dia_sem(j,i,2016))
            dict_sem[str(j)+'-'+str(i)].append(semana)
            if dia_sem(j,i,2016) == 7:
                semana += 1
    df_orders = df_orders.sort_values('order_id')
    date = df_orders["date"]
    day_sem = []
    sem = []
    semana = 1
    for d in date:
        d = str(d)
        d = d.split('-')
        c = dict_sem[str(int(d[2].split(' ')[0]))+'-'+str(int(d[1]))]
        day_sem.append(c[0])
        sem.append(c[1])
    df_orders.insert(3,'sem',sem)
    details = list(df_details.loc[:,'order_id'])
    sem_1 = []
    for i in details:
        sem_1.append(list(df_orders.loc[df_orders.order_id == i]['sem'].tolist())[0])
    df_details.insert(3,'sem',sem_1)
    variables = ['quantity']
    columnas = ['pizza_id','sem'] + variables
    df_selec = df_details.loc[:, columnas]

    pizzas = []
    for j in range(1,53):
        p = []
        for i in list(df_selec.index):
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
    dict_p = {}
    for p in pizzas:
        count = {}
        claves = list(dict.fromkeys(p))
        for c in claves:
            count[c] = p.count(c)
        total.append(count)
    for d in df_types["pizza_type_id;name;category;ingredients"]:
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

    def comprobar_s(ing,dic):
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
            no_salsa = comprobar_s('Tomato Sauce',list(i_sem.keys()))
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

    pizzas = []
    for j in range(1,53):
        p = []
        for i in list(df_selec.index):
            if df_selec['sem'][i] == j:
                for k in range(int(df_selec['quantity'][i])):
                    p.append(df_selec['pizza_id'][i])
        sm = []
        for tam in p:
            sm.append(tam)
        pizzas.append(sm)


    list_count = []
    pi = ['bbq_ckn_s','bbq_ckn_m','bbq_ckn_l','cali_ckn_s','cali_ckn_m','cali_ckn_l','ckn_alfredo_s','ckn_alfredo_m','ckn_alfredo_l','ckn_pesto_s','ckn_pesto_m','ckn_pesto_l','southw_ckn_s','southw_ckn_m','southw_ckn_l','thai_ckn_s','thai_ckn_m','thai_ckn_l','big_meat_s','big_meat_m','big_meat_l','classic_dlx_s','classic_dlx_m','classic_dlx_l','hawaiian_s','hawaiian_m','hawaiian_l','ital_cpcllo_s','ital_cpcllo_m','ital_cpcllo_l','napolitana_s','napolitana_m','napolitana_l','pep_msh_pep_s','pep_msh_pep_m','pep_msh_pep_l','pepperoni_s','pepperoni_m','pepperoni_l','the_greek_s','the_greek_m','the_greek_l','the_greek_xl','the_greek_xxl','brie_carre_s','calabrese_s','calabrese_m','calabrese_l','ital_supr_s','ital_supr_m','ital_supr_l','peppr_salami_s','peppr_salami_m','peppr_salami_l','prsc_argla_s','prsc_argla_m','prsc_argla_l','sicilian_s','sicilian_m','sicilian_l','soppressata_s','soppressata_m','soppressata_l','spicy_ital_s','spicy_ital_m','spicy_ital_l','spinach_supr_s','spinach_supr_m','spinach_supr_l','five_cheese_s','five_cheese_m','five_cheese_l','four_cheese_s','four_cheese_m','four_cheese_l','green_garden_s','green_garden_m','green_garden_l','ital_veggie_s','ital_veggie_m','ital_veggie_l','mediterraneo_s','mediterraneo_m','mediterraneo_l','mexicana_s','mexicana_m','mexicana_l','spin_pesto_s','spin_pesto_m','spin_pesto_l','spinach_fet_s','spinach_fet_m','spinach_fet_l','veggie_veg_s','veggie_veg_m','veggie_veg_l']

    for p in pizzas:
        p_count = {}
        for c in pi:
            try:
                p_count[c] = p.count(c)
            except:
                p_count[c] = 0
        list_count.append(p_count)
        
    data = {'pizzas': deepcopy(pi)}
    i = 0
    while i < len(list_count):
        data[f'sem{i+1}'] = list(list_count[i].values())
        i += 1

    for c in data.keys():
        if c == 'pizzas':
            data[c].append('Total')
        else:
            sum = 0
            for val in data[c]:
                sum += val
            data[c].append(sum)
    
    df_count = pd.DataFrame(data=data)

    cost = {}
    for p in pi:
        if p != 'Total':
            cost[p]=list(df_pizzas.loc[df_pizzas.pizza_id == p].values)[0][3]

    list_price = []
    pi = pi[:-1]
    for p in pizzas:
        p_price = {}
        for c in pi:
            try:
                p_price[c] = p.count(c)*cost[c]
            except:
                p_price[c] = 0
        list_price.append(p_price)
    data2 = {'pizzas': deepcopy(pi)}
    
    i = 0
    while i < len(list_price):
        data2[f'sem{i+1}'] = list(list_price[i].values())
        i += 1
        
    for c in data2.keys():
        
        if c == 'pizzas':
            data2[c].append('Total')
        else:
            sum = 0
            for val in data[c]:
                sum += val
            data2[c].append(sum)
            
    df_price = pd.DataFrame(data=data2)

    keys = list(i_sem_total[0].keys())
    keys.sort()
    for i in range(len(i_sem_total)):
        dic = i_sem_total[i]
        for k in keys:
            if not k in dic.keys():
                dic[k] = 0
        dic = {key: val for key, val in sorted(dic.items(), key = lambda ele: ele[0], reverse = True)}
        i_sem_total[i] = dic

    data3 = {'ingredientes':list(i_sem_total[0].keys())}
    for i in range(len(i_sem_total)):
        data3[f'sem{i+1}'] = list(i_sem_total[i].values())
        
    df_ing = pd.DataFrame(data=data3)

    return df_ing, df_count, df_price


def load(df_ing, df_count, df_price):
    with pd.ExcelWriter('mavens.xlsx', engine='xlsxwriter') as writer:
        df_ing.to_excel(writer, sheet_name='Reporte de Ingredientes')
        df_count.to_excel(writer, sheet_name='Reporte de ventas')
        df_price.to_excel(writer, sheet_name='Reporte de ingresos')


if __name__ == '__main__':
    df_types, df_pizzas, df_orders, df_details = extract()
    df_ing, df_count, df_price = transform(df_types, df_pizzas, df_orders, df_details)
    load(df_ing, df_count, df_price)
