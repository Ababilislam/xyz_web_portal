def new_web_order_entry():  
    response.title='New Order'
    from datetime import datetime
    c_id=session.cid
    depot_id = session.depot_id
    if depot_id =="" or depot_id=="None" or depot_id==None:
        depot_id = " "
    user_id = session.user_id
    depot_name = session.user_depot_name
    if depot_name =="" or depot_name=="None" or depot_name==None:
        depot_name = " "
    save_button =request.vars.submit_btn
    cancel_btn =request.vars.cancel_btn
    update_btn =request.vars.update_btn
    submit_all_button =request.vars.submit_all_btn
    invoice_counter_record = ''
    current_datetime = date_fixed
    year = current_datetime.year
    month = current_datetime.month
    first_date_of_month = datetime(year, month, 1)
    first_date_str = first_date_of_month.strftime("%Y-%m-%d")

    current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    status = 'Draft'
    temp_status = 'Submitted'
    order_sl = 0
    item_per_unit = 1
    total_depot_stock_qty = 0
    depot_row_id = 0
    try:
        page=int(request.args[0])
    except:
        page=0

    last_order_sl_query = f"select sl from sm_order_head where cid = '{c_id}' order by id desc limit 1;"
    # return last_order_sl_query
    last_order_sl = db.executesql(last_order_sl_query,as_dict=True)
    # order_sl = last_order_sl[0]['sl']
    if session.order_sl =="" or session.order_sl==None:
        order_sl = request.vars.req_sl
    else:
        order_sl = session.order_sl
    

    #================================ SAVE BUTTON CLICK =================================#

    if save_button == 'Save':
        order_sl = str(request.vars.order_sl_id).replace('None', '')
        sales_date = request.vars.sales_date_id
        pay_type = str(request.vars.pay_type).strip().replace('None', '')
        note = str(request.vars.note_id).strip().replace('None', '')
        shift = str(request.vars.shift).strip().replace('None', '')
        delivery_date = str(request.vars.delivery_date_id).strip().replace('None', '')
        item_id_check = str(request.vars.item_id)
        # return item_id_check
        quantity = request.vars.qty_id
        # return f"{order_sl}, {sales_date}, {pay_type}, {note}, {shift},{delivery_date}, {item_id_check}"
        category_id = ''
        category_id_sp = ''
        rep_category = ''
        market_id = ''
        market_name = ''
        vat = 0
        item_unit = ''
        item_carton = 0
        order_media = 'Web'
        store_id = ''
        store_name = ''
        flag_data = 0
        field1 = 'ORDER'
        field2 = 1
        visit_type = 'unscheduled'
        order_count = 0
        user_type = ''
        client_cat = ''
        invoice_ref = 0
        mobile_no = 0
        created__on = current_datetime

        try:
            client_id =str(request.vars.client).strip().split('|')[0]
            client_name =str(request.vars.client).strip().split('|')[1]
        except:
            client_id = ''
            client_name = ''

        try:
            rep_id =str(request.vars.rep).strip().split('|')[0]
            rep_name =str(request.vars.rep).strip().split('|')[1]
        except:
            rep_id = ''
            rep_name = ''

        try:
            region_id =str(request.vars.region).strip().split('|')[0]
            region_name =str(request.vars.region).strip().split('|')[1]
        except:
            region_id = ''
            region_name = ''

        try:
            zone_id =str(request.vars.zone).strip().split('|')[0]
            zone_name =str(request.vars.zone).strip().split('|')[1]
        except:
            zone_id = ''
            zone_name = ''

        try:
            area_id =str(request.vars.area).strip().split('|')[0]
            area_name =str(request.vars.area).strip().split('|')[1]
        except:
            area_id = ''
            area_name = ''
        try:
            territory_id =str(request.vars.territory).strip().split('|')[0]
            territory_name =str(request.vars.territory).strip().split('|')[1]
        except:
            territory_id = ''
            territory_name = ''

        try:
            item_id =str(request.vars.item_id).strip().split('|')[0]
            item_name =str(request.vars.item_id).strip().split('|')[1]
        except:
            item_id = ''
            item_name = ''

        region = str(request.vars.region).replace('None', '')
        zone = str(request.vars.zone).replace('None', '')
        area = str(request.vars.area).replace('None', '')
        territory = str(request.vars.territory).replace('None', '')
        client = str(request.vars.client).replace('None', '')
        rep = str(request.vars.rep).replace('None', '')
        session.order_sl = order_sl
        session.sales_date = sales_date
        session.region = region
        session.zone = zone
        session.area = area
        session.territory = territory
        session.client = client
        session.rep = rep
        session.pay_type = pay_type
        session.status = status
        session.shift = shift
        session.delivery_date = delivery_date
        session.note = note

        if quantity == '0' or quantity == 0:
            session.order_sl = order_sl
            session.flash = 'Quantity should not be 0'
            redirect(URL(c='web_order',f='new_web_order_entry'))

        price = 0
        discount_percentage = 0.0
        total_price = 0

        # get_store_info_sql = f"SELECT store_id, store_name FROM sm_depot_store where cid = '{c_id}' and depot_id = '{depot_id}' and store_name = 'Commercial' group by store_id limit 1 ;"
        # get_store_info = db.executesql(get_store_info_sql, as_dict=True)
        # get_store_info_str = get_store_info[0]
        # store_id = str(get_store_info_str['store_id'])
        # store_name = str(get_store_info_str['store_name'])

        # get_user_type_sql = "SELECT user_type, mobile_no FROM sm_rep where cid = '"+c_id+"' and rep_id = '"+rep_id+"' group by rep_id limit 1 ;"
        # get_user_type = db.executesql(get_user_type_sql, as_dict=True)
        # for r in range(len(get_user_type)):
        #     repRecordsStr = get_user_type[r]
        #     user_type = str(repRecordsStr['user_type'])
        #     mobile_no = str(repRecordsStr['mobile_no'])

        # userAreaRecords = 'select rep_category from sm_rep_area where cid="' + c_id + '" and rep_id="' + rep_id + '";'
        # userAreaRecords = db.executesql(userAreaRecords, as_dict=True)
        # for o in range(len(userAreaRecords)):
        #     userAreaRecordsStr = userAreaRecords[o]
        #     rep_category = str(userAreaRecordsStr['rep_category'])
        # market_id = rep_category
        # market_name = rep_category

        # client_Records_sql = 'select category_id from sm_client where cid="' + c_id + '" and client_id="' + client_id + '";'
        # client_Records = db.executesql(client_Records_sql, as_dict=True)
        # for o in range(len(client_Records)):
        #     clientRecordsStr = client_Records[o]
        #     client_cat = str(clientRecordsStr['category_id'])
        

        select_item_price_sql = "SELECT category_id, category_id_sp, price, vat_amt, total_amt, unit_type, item_carton from sm_item where cid = '"+c_id+"' and name = '"+str(item_id_check)+"' group by name limit 1;"
        select_item_price = db.executesql(select_item_price_sql, as_dict=True)
        for a in range(len(select_item_price)):
            item_record_data = select_item_price[a]
            category_id = str(item_record_data['category_id'])
            category_id_sp = str(item_record_data['category_id_sp'])
            item_unit = str(item_record_data['unit_type'])
            item_carton = str(item_record_data['item_carton'])
            price = float(item_record_data['price'])
            vat = float(item_record_data['vat_amt'])
            total_amt = float(item_record_data['total_amt'])

        check_exits_sl_sql = "SELECT sl from sm_order_head where cid = '"+c_id+"' AND sl = '"+str(order_sl)+"' group by sl limit 1;"
        # return check_exits_sl_sql
        check_exits_sl = db.executesql(check_exits_sl_sql, as_dict=True)
        # return f"cid:{c_id}, depot_id:{depot_id}, depot_name:{depot_name}, order_sl:{order_sl}, store_id: {store_id}, store_name: {store_name}, client_id: {client_id}, client_name: {client_name}, rep_id: {rep_id}, rep_name:{rep_name}, sales_date:{sales_date}, current_datetime:{current_datetime}, delivery_date:{delivery_date}, collection_date:{delivery_date}, pay_type: {pay_type}, territory_id:{territory_id}, territory_name:{territory_name}, region_id:{region_id}, region_name:{region_name},zone_id: {zone_id},zone_name: {zone_name}, area_id:{area_id}, area_name:{area_name}, territory_id:{territory_id}, territory_name:{territory_name}, status:{status}, order_media:{order_media},first_date_str:{first_date_str},flag_data: {str(flag_data)}, visit_type:{visit_type},user_type:{user_type}, client_cat:{client_cat},invoice_ref:{ str(invoice_ref)},field1: {field1}, field2:{str(field2)}, shift:{shift}, market_id:{market_id}, market_name:{market_name}, mobile_no:{str(mobile_no)}"
        if len(check_exits_sl) == 0:
            order_head_insert_sql = "INSERT INTO sm_order_head (cid, depot_id, depot_name, sl, store_id, store_name, client_id, client_name, rep_id, rep_name, order_date, order_datetime, delivery_date, collection_date, payment_mode, area_id, area_name, level0_id, level0_name, level1_id, level1_name, level2_id, level2_name, level3_id, level3_name, status, order_media, ym_date, flag_data, visit_type, user_type, client_cat, invoice_ref, field1, field2, created_by, market_id, market_name, mobile_no) values('"+c_id+"', '"+depot_id+"', '"+depot_name+"', '"+order_sl+"', '"+store_id+"', '"+store_name+"', '"+client_id+"', '"+client+"', '"+rep_id+"', '"+rep+"', '"+sales_date+"', '"+current_datetime+"', '"+delivery_date+"', '"+delivery_date+"', '"+pay_type+"', '"+territory_id+"', '"+territory_name+"', '"+region_id+"', '"+region_name+"', '"+zone_id+"', '"+zone_name+"', '"+area_id+"', '"+area_name+"', '"+territory_id+"', '"+territory_name+"', '"+status+"', '"+order_media+"', '"+first_date_str+"', '"+str(flag_data)+"', '"+visit_type+"','"+user_type+"', '"+client_cat+"', '"+str(invoice_ref)+"', '"+field1+"','"+str(field2)+"', '"+shift+"', '"+market_id+"', '"+market_name+"', '"+str(mobile_no)+"') "; 
            # print(order_head_temp_insert_sql) 
            # return order_head_temp_insert_sql
            order_head_temp_insert = db.executesql(order_head_insert_sql)

        same_item_check__sql = "SELECT item_name, quantity from sm_order where cid = '"+c_id+"' AND sl = '"+str(order_sl)+"' AND item_name = '"+str(item_id_check)+"' group by item_name"
        # return same_item_check__sql
        check_same_item = db.executesql(same_item_check__sql, as_dict=True)

        if len(check_same_item) > 0:
            session.flash = 'Please Select Different Item.'
            redirect(URL(c='web_order',f='new_web_order_entry'))
        else:
            total_price = int(quantity) * float(price)
            total_price = float(total_price)
            
            order_details_insert_sql = f"INSERT INTO sm_order (cid, vsl, depot_id, depot_name, sl, store_id, store_name, client_id, client_name, rep_id, rep_name, order_date, order_datetime, delivery_date, collection_date, payment_mode, area_id, area_name, level0_id, level0_name, level1_id, level1_name, level2_id, level2_name, level3_id, level3_name, status, item_id, item_name, category_id, category_id_sp, price, quantity, item_vat, item_unit, item_carton, order_media, ym_date, invoice_ref, created_by, market_id, market_name, flag_data, field1, field2) values('{c_id}', '{order_sl}', '{depot_id}', '{depot_name}', '{order_sl}', '{store_id}', '{store_name}', '{client_id}', '{client}', '{rep_id}', '{rep}', '{sales_date}', '{current_datetime}', '{delivery_date}', '{delivery_date}', '{pay_type}', '{territory_id}', '{territory_name}', '{region_id}', '{region_name}', '{zone_id}', '{zone_name}', '{area_id}', '{area_name}', '{territory_id}', '{territory_name}', '{status}', '{item_id}', '{item_id_check}', '{category_id}', '{category_id_sp}', {price}, {quantity}, {vat}, '{item_unit}', {item_carton}, '{order_media}', '{first_date_str}', '{invoice_ref}', '{shift}', '{market_id}', '{market_name}', '{flag_data}','{field1}', '{field2}');"
            # return order_details_insert_sql
            order_details_insert = db.executesql(order_details_insert_sql)
            session.flash = 'Item Insert Successfully'
            redirect(URL(c='web_order',f='new_web_order_entry'))


    #================================ UPDATE BUTTON CLICK =================================#
    
    if update_btn:
        record_id = request.args(0)
        actual_price = request.args(1)
        item_id = request.args(2)
        total_update_price = 0
        update_qty = request.vars.quantity_id

        if update_qty == 0 or update_qty =='0':
            session.flash = 'Quantity should not be 0'
            redirect(URL(c='web_order',f='new_web_order_entry'))

        total_update_price = float(actual_price) * int(update_qty)
        total_update_price = float(total_update_price)
        update_qty_sql= " Update sm_order Set quantity ='"+str(update_qty)+"' WHERE cid = '"+c_id+"' and id = '"+str(record_id)+"' LIMIT 1;"  
        update_qty = db.executesql(update_qty_sql)
        session.flash = 'Quantity updated Successfully'
        redirect(URL(c='web_order',f='new_web_order_entry'))

    #================================ SUBMIT BUTTON CLICK =================================#

    if submit_all_button == 'Submit':

        get_order_sl = request.args(0)
        net_total = request.args(1)
        status = 'Submitted'

        select_sm_order_head_record_sql = "SELECT * FROM sm_order_head where cid = '"+c_id+"' and sl = '"+get_order_sl+"' group by sl limit 1"
        select_sm_order_head_record = db.executesql(select_sm_order_head_record_sql, as_dict=True)
        update_head_sql = f"UPDATE sm_order_head SET status='{status}' WHERE cid = '{c_id}' and sl='{get_order_sl}';" 
        # return update_head_sql
        db.executesql(update_head_sql)

        get_order_sql = f"SELECT * FROM `sm_order` WHERE cid='{c_id}' and sl = '{get_order_sl}' and status='draft';"
        order_records = db.executesql(get_order_sql,as_dict=True)
        
        update_order_sql = f"UPDATE sm_order SET status='{status}' WHERE cid='{c_id}' and sl = '{get_order_sl}';"
        db.executesql(update_order_sql)
    #================================ INVOICE BUTTON CLICK =================================#
        

        session.order_sl = int(get_order_sl) +1
        session.sales_date = ''
        session.region = ''
        session.zone = ''
        session.area = ''
        session.territory = ''
        session.client = ''
        session.rep = ''
        session.pay_type = ''
        session.status = ''
        session.shift = ''
        session.delivery_date = ''
        session.note = ''
        session.flash = 'Invoiced Successfully'
        redirect (URL('web_order','new_web_order_entry')) 

    #================================ CANCEL BUTTON CLICK =================================#

    if cancel_btn == 'Order Cancel':
        get_order_sl = request.args(0)
        status = 'Cancelled'
        select_sm_order_head_record_sql = "SELECT * FROM sm_order_head where cid = '"+c_id+"' and sl = '"+get_order_sl+"' group by sl limit 1"
        select_sm_order_head_record = db.executesql(select_sm_order_head_record_sql, as_dict=True)
        if not select_sm_order_head_record:
            session.flash = 'Order doesnot exist'
            redirect(URL(c='web_order',f='new_web_order_entry'))
        update_head_sql = f"UPDATE sm_order_head SET status='{status}' WHERE cid = '{c_id}' and sl='{get_order_sl}';" 
        # return update_head_sql
        db.executesql(update_head_sql)

        get_order_sql = f"SELECT * FROM `sm_order` WHERE cid='{c_id}' and sl = '{get_order_sl}' and status='draft';"
        order_records = db.executesql(get_order_sql,as_dict=True)
        if not order_records:
            session.flash = 'Order doesnot exist'
            redirect(URL(c='web_order',f='new_web_order_entry'))
        
        update_order_sql = f"UPDATE sm_order SET status='{status}' WHERE cid='{c_id}' and sl = '{get_order_sl}';"
        db.executesql(update_order_sql)

        session.order_sl = ''
        session.sales_date = ''
        session.region = ''
        session.zone = ''
        session.area = ''
        session.territory = ''
        session.client = ''
        session.rep = ''
        session.pay_type = ''
        session.status = ''
        session.shift = ''
        session.delivery_date = ''
        session.note = ''
        session.flash = 'Canceled Successfully'
        redirect (URL('web_order','new_web_order_entry'))

    order_temp_record_sql = f"SELECT * from sm_order WHERE cid ='{c_id}' and sl = '{order_sl}';"
    order_record = db.executesql(order_temp_record_sql, as_dict=True)

    return dict(current_datetime = current_datetime, order_sl=order_sl, order_temp_record=order_record, status=status,page=page)

    return locals()



def order_delete():
    c_id=session.cid
    # depot_id = session.depot_id
    response.title='Order Delete'
    record_id = request.args(0)
    order_sl = request.args(1)
    
    delete_sql = "DELETE from sm_order where cid = '"+c_id+"' and id = '"+record_id+"' limit 1;"
    records = db.executesql(delete_sql)
    check_exits_order_sl_sql = "SELECT sl from sm_order where cid = '"+c_id+"' and sl = '"+str(order_sl)+"' group by sl"
    check_exits_order_sl = db.executesql(check_exits_order_sl_sql, as_dict=True)
    if len(check_exits_order_sl) == 0:
        delete_sm_order_head_sql = "DELETE from sm_order_head where cid = '"+c_id+"' and sl = '"+str(order_sl)+"';"
        db.executesql(delete_sm_order_head_sql)

    session.flash = 'Deleted Successfully'
    redirect (URL('web_order','new_web_order_entry'))



def get_item_list():
    retStr = ''
    cid = session.cid
    # return cid
    
    sql_query = f"SELECT name from sm_item where cid = '{cid}' order by name"

    # print('get_all_item_list: sql_query: ', sql_query)
    # return sql_query
    rows = db.executesql(sql_query, as_dict = True)

    for idx in range(len(rows)):
        name = rows[idx]['name']
        if retStr == '':
            retStr =  name
        else:
            retStr += ',' + name

    return retStr