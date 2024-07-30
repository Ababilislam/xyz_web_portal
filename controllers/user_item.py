def user_item():
    response.title ="Item"
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    
    session.item_id_filter = ''
    session.ym_date_filter=''
    
    # pagging
    reqPage = len(request.args)

    session.items_per_page = 20
    if reqPage:
        page = int(request.args[0])
    else:
        page = 0
    items_per_page = session.items_per_page
    if(page==0):
        limitby = (page * items_per_page, (page + 1) * items_per_page)
    else:
        limitby = ((page* items_per_page), items_per_page)
    # --------end paging
    btn_filter_item=request.vars.btn_filter_item
    btn_all = request.vars.btn_all
    item_id_filter = request.vars.item_id_filter


    condition = ''
    # return c_id
    
    cid=session.cid
    user_id=session.user_id
   
    
    if btn_filter_item:
        item_id_filter = item_id_filter.strip()
        # return item_id_filter
        
        item_name = item_id_filter
        # return item_name
        condition = f" and name ='{item_name}'"

        session.item_id_filter = item_id_filter
        session.condition=condition
    
    if btn_all:
        condition = ""
        session.item_id_filter = ''


    itemRows_sql = "select * from sm_item where cid = '"+str(cid)+"'  "+condition+" ORDER BY id DESC limit %d, %d;" % limitby
    # return itemRows_sql
    itemRows = db.executesql(itemRows_sql, as_dict=True)
  
    # return 22
    
    total_record_sql = f"SELECT COUNT(id) AS total FROM sm_item WHERE cid='{cid}' {condition} ORDER BY id ASC;"
    # return total_record_sql
    total_record = db.executesql(total_record_sql, as_dict = True)
    total_rec = total_record[0]['total']
    
    session.condition=condition
   
    return dict(itemRows=itemRows,page=page,items_per_page=items_per_page,total_rec=total_rec,)


def item_list_download():
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    c_id = session.cid
    condition = ''
    condition = session.condition

    download_sql = "select * from sm_item where cid = '"+c_id+"' "+condition+";"
    download_records = db.executesql(download_sql, as_dict=True)
    
    myString = 'Item List\n\n'
    myString += 'item_name,Stock Quantity,TP Amount,Vat Amount,Total Amount\n'
    total=0
    attTime = ''
    totalCount = 0
    for i in range(len( download_records)):
        recordsStr =  download_records[i]
        # item_id=str(recordsStr["item_id"])
        name=str(recordsStr["name"])
        qty=str(recordsStr["stock_quantity"])
        tp=str(recordsStr["price"])
        if tp=='' or tp==None or tp=="None":
            tp='0'
        vat_amt=str(recordsStr["vat_amt"])
        total_amnt = float((int(qty)*float(tp))+(int(qty)*float(vat_amt)))

        


        myString +=  str(name) + ','  + str(qty) + ',' + str(tp) + ',' + str(vat_amt)+ ',' + str(total_amnt) +'\n'

    # Save as csv
    import gluon.contenttype
    response.headers['Content-Type'] = gluon.contenttype.contenttype('.csv')
    response.headers['Content-disposition'] = 'attachment; filename=download_Item.csv'
    return str(myString) 



def get_all_item_list():
    retStr = ''
    cid = session.cid
    # return cid
    
    sql_query = f"SELECT name from sm_item where cid = '{cid}' order by name"

    # print('get_all_item_list: sql_query: ', sql_query)
    # return sql_query
    rows = db.executesql(sql_query, as_dict = True)

    # print('rows: ',len(rows))

    for idx in range(len(rows)):
        
        name = rows[idx]['name']
        # return name
        
        if retStr == '':
            retStr = name
        else:
            retStr += ',' + name

    return retStr