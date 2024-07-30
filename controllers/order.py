
def user_order():
    response.title = 'Order'
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    
    session.item_id_filter = ''
    
    
    # pagging
    reqPage = len(request.args)
    session.items_per_page=20
    if reqPage:
        page=int(request.args[0])
    else:
        page=0
    items_per_page=session.items_per_page
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    # --------end paging
    btn_filter_item=request.vars.btn_filter_item
    btn_all = request.vars.btn_all
    item_id_filter = request.vars.item_id_filter


    condition = ''
    cid=session.cid
    user_id=session.user_id
    user_name=session.name
    # print(session)
    # return user_name

    if user_name:
        condition = f"and created_by='{user_name}'"
    
    if btn_filter_item:
        from_date = request.vars.from_date
        to_date = request.vars.to_date
        # return from_date, to_date
        # return item_id_filter
        
        
        condition = f" and order_date >='{from_date}' and order_date <='{to_date}'"

        session.from_date = from_date
        session.to_date = to_date
        session.condition=condition
    
    if btn_all:
        condition = ""
        session.from_date = ""
        session.to_date = ""

    order_sl_sql = f"select * from sm_order_head where cid='{cid}' {condition} order by sl DESC limit %d, %d;" % limitby
    # return order_sl_sql
    itemRows = db.executesql(order_sl_sql, as_dict=True)
    
    
    
    total_record_sql = f"select count(sl) as total from sm_order_head where cid='{cid}' {condition} ORDER BY sl ASC;"
    # return total_record_sql
    total_record = db.executesql(total_record_sql, as_dict = True)
    total_rec = total_record[0]['total']
    
    session.condition=condition
   
    return dict(itemRows=itemRows,page=page,items_per_page=items_per_page,total_rec=total_rec)


def add_order_sl():
    cid = session.cid
    if (cid=='' or cid==None):
        redirect (URL('default','index'))
    
    last_sl_query = f"SELECT `sl` FROM `sm_order_head` WHERE cid='{cid}' ORDER BY sl DESC;"
    last_sl = db.executesql(last_sl_query,as_dict=True)

    last_order_sl=last_sl[0]['sl']
    order_sl = int(last_order_sl)+1
    rep_name=session.name
    order_date =str(date_fixed)[0:10]
    # return order_date
    order_date_time =str(date_fixed)
    status ="Submitted"
    create_on=str(date_fixed)
    created_by = session.name
    check_order_sql = f"select * from sm_order_head where cid='{cid}' and sl='{order_sl}' limit 1;"
    # return check_order_sql
    check_order = db.executesql(check_order_sql)
    if not check_order:
        insert_sql = f"INSERT INTO `sm_order_head`(`cid`, `sl`, `rep_name`, `order_date`, `order_datetime`,  `status`,  `created_on`, `created_by`) VALUES ('{cid}','{order_sl}','{rep_name}','{order_date}','{order_date_time}','{status}','{create_on}','{created_by}')"
         # return insert_sql
        db.executesql(insert_sql)
        session.flash = "Order serial created"
        redirect(URL('user_order'))
    else:
        response.flash = "order serial already exists"
    


def order_details():
    response.title = 'Add Order'
    cid = session.cid
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    
    btn_update=request.vars.btn_update
    try:
        page=int(request.args[0])
    except:
        page=0
    # # pagination 
    # reqPage = len(request.args)

    # session.items_per_page = 20
    # if reqPage:
    #     page = int(request.args[0])
    # else:
    #     page = 0
    # items_per_page = session.items_per_page
    # if(page==0):
    #     limitby = (page * items_per_page, (page + 1) * items_per_page)
    # else:
    #     limitby = ((page* items_per_page), items_per_page)
    # # --------end paging

    depot_id=''
    depot_name=''    
    req_sl=request.vars.req_sl    
    rowid=0
    # Depot ID
    
    invoice_no=''
    status='Submitted'  #'Draft'
    client_id=''
    rep_id=''
    order_date=''
    delivery_date=''
    order_datetime=str(date_fixed)[0:19]
    payment_mode=''
    note=''
    
    client_name=''
    rep_name=''
    visit_sl=0
    invoice_ref=0
    
    level0_id=''
    level0_name=''
    level1_id=''
    level1_name=''
    level2_id=''
    level2_name=''
    level3_id=''
    level3_name=''

    h_record_sql = f"SELECT * FROM `sm_order_head` WHERE cid='{cid}' and sl = '{req_sl}' LIMIT 1;"
    # return h_record_sql
    h_record = db.executesql(h_record_sql, as_dict=True)
    if h_record:
        rowid=h_record[0]['id']
        depot_id=h_record[0]['depot_id']
        depot_name=h_record[0]['depot_name']      
        sl=h_record[0]['sl']
        status=h_record[0]['status']
        client_id=h_record[0]['client_id']
        rep_id=h_record[0]['rep_id']
        order_date=h_record[0]['order_date']
        order_datetime=str(h_record[0]['order_datetime'])[0:19]
        delivery_date=h_record[0]['delivery_date']        
        client_name=h_record[0]['client_name']
        rep_name=h_record[0]['rep_name']    
        visit_sl=h_record[0]['id']
        payment_mode=h_record[0]['payment_mode']
        note=h_record[0]['note']
        invoice_ref=h_record[0]['invoice_ref']
                
        level0_id=h_record[0]['level0_id']
        level0_name=h_record[0]['level0_name']
        level1_id=h_record[0]['level1_id']
        level1_name=h_record[0]['level1_name']
        level2_id=h_record[0]['level2_id']
        level2_name=h_record[0]['level2_name']
        level3_id=h_record[0]['level3_id']
        level3_name=h_record[0]['level3_name']

    record_sql = f"SELECT * FROM `sm_order` WHERE cid='{cid}' and sl = '{req_sl}' order by item_name"
    # return record_sql
    record = db.executesql(record_sql,as_dict=True)
    
    
    return dict(rowid=rowid,visit_sl=visit_sl,records=record,depot_id=depot_id,depot_name=depot_name,sl=sl,invoice_ref=invoice_ref,client_id=client_id,rep_id=rep_id,client_name=client_name,rep_name=rep_name,order_date=order_date,order_datetime=order_datetime,delivery_date=delivery_date,status=status,level0_id=level0_id,level0_name=level0_name,level1_id=level1_id,level1_name=level1_name,level2_id=level2_id,level2_name=level2_name,level3_id=level3_id,level3_name=level3_name,payment_mode=payment_mode,note=note,page=page)
    
   
    # return dict(itemRows=itemRows,order_sl=order_sl,page=page)



    
    return dict()
    


def get_all_order_list():
    retStr = ''
    cid = session.cid
    name = session.name
    # return cid
    
    sql_query = f"select * from sm_order where cid = '{cid}' and updated_by='{name}'  ORDER BY id ASC;"

    # print('get_all_item_list: sql_query: ', sql_query)
    # return sql_query
    rows = db.executesql(sql_query, as_dict = True)

    # print('rows: ',len(rows))

    for idx in range(len(rows)):
        # item_id = str(row.item_id)
        # name = str(row.name).replace('|', ' ').replace(',', ' ')
        try:
            item_name = rows[idx]['item_name']
        except:
            item_name=""
        
        # return(item_id, ' :: ', name)
        
        if retStr == '':
            retStr = item_name
        else:
            retStr += ',' + item_name

    return retStr





def order():
    response.title = 'Order'
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    
    session.item_id_filter = ''
    
    
    # pagging
    reqPage = len(request.args)
    session.items_per_page=20
    if reqPage:
        page=int(request.args[0])
    else:
        page=0
    items_per_page=session.items_per_page
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    # --------end paging
    btn_filter_order=request.vars.btn_filter_order
    btn_all = request.vars.btn_all
    item_id_filter = request.vars.item_id_filter


    condition = ''
    cid=session.cid
    user_id=session.user_id
    user_name=session.name
    # print(session)
    # return user_name

   
    
    if btn_filter_order:
        # return "aa"
        order_date = request.vars.order_date
        # return order_date
        mobile = request.vars.mobile
        # return mobile
        # return order_date, mobile
        # return item_id_filter
        
        # if order_date !="" or order_date != None:
        if order_date:
            condition += f" and order_date ='{order_date}'"
        if mobile:
            # return "ab"
            condition += f" and mobile_no='{mobile}'"

        session.order_date = order_date
        session.mobile = mobile
        session.condition=condition
        # return condition
    if btn_all:
        condition = ""
        session.order_date = ""
        session.mobile = ""

    order_sl_sql = f"select * from sm_order_head where cid='{cid}' {condition} order by sl DESC limit %d, %d;" % limitby
    # return order_sl_sql
    itemRows = db.executesql(order_sl_sql, as_dict=True)
    
    total_rec = len(itemRows)

    last_order_sql = f"select sl from sm_order_head where cid='{cid}' order by id desc limit 1;"
    # return last_order_sql
    last_order = db.executesql(last_order_sql, as_dict = True)
    last_order_sl = last_order[0]['sl'] if last_order else '0'
    last_order_sl =last_order_sl+1
    # return last_order_sl
    
    
    session.condition=condition
   
    return dict(itemRows=itemRows,page=page,items_per_page=items_per_page,total_rec=total_rec,last_order_sl=last_order_sl)



def download_order():
    cid = session.cid
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    condition = ''
    condition = session.condition

    download_sql = "select * from sm_order where cid = '"+cid+"' "+condition+";"
    # return download_sql
    download_records = db.executesql(download_sql, as_dict=True)
    
    myString = 'Order List\n\n'

    myString += 'item Serial,item Name,Quantity,TP Amount,Vat Amount,Order Date,Delivery Date,Status\n'
    total=0
    attTime = ''
    totalCount = 0
    for records_ov_dict in itemRows:
        id=str(records_ov_dict["id"])
        item_sl=str(records_ov_dict["sl"])
        item_name=str(records_ov_dict["item_name"])
        quantity=str(records_ov_dict["quantity"])
        price=str(records_ov_dict["price"])
        vat=str(records_ov_dict["item_vat"])
        
        order_date=str(records_ov_dict["order_date"])
        delevery_date=str(records_ov_dict["delivery_date"])
        status=str(records_ov_dict["status"])
        
        


        myString += str(sl) + ','  + str(qty) + ',' + str(tp) + ',' + str(vat_amt) +'\n'

    # Save as csv
    import gluon.contenttype
    response.headers['Content-Type'] = gluon.contenttype.contenttype('.csv')
    response.headers['Content-disposition'] = 'attachment; filename=download_Item.csv'
    return str(myString) 
    
    
    
    
    order_sl_sql = f"select sl from sm_order_head where cid='{cid}' and order_date >='{from_date}' and order_date <='{to_date}' order by sl desc";
    order_sl = db.executesql(order_sl_sql, as_dict=True)
    sl_list = []
    for i in order_sl:
        sl_list.append(i['sl'])
    
    sl_placeholders = ''







def get_all_item_list():
    retStr = ''
    cid = session.cid
    # return cid
    
    sql_query = f"SELECT item_id,name,price from sm_item where cid = '{cid}' order by name"

    # print('get_all_item_list: sql_query: ', sql_query)
    # return sql_query
    rows = db.executesql(sql_query, as_dict = True)

    # print('rows: ',len(rows))

    for idx in range(len(rows)):
        # item_id = str(row.item_id)
        # name = str(row.name).replace('|', ' ').replace(',', ' ')
        try:
            item_id = rows[idx]['item_id']
        except:
            item_id=""
        name = rows[idx]['name']
        # return(item_id, ' :: ', name)
        try:
            price = rows[idx]['price']
        except:
            price = " "
        if price =="" or price==None:
            price=0
        if item_id=="" or item_id==None:
            item_id = " "
        if retStr == '':
            retStr = name +"|" + str(price)
        else:
            retStr += ',' + name +"|" + str(price)

    return retStr