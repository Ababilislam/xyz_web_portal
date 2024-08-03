def new_web_order_entry():  
    response.title='New Order'
    from datetime import datetime
    c_id=session.cid
     
    save_btn=request.vars.save
    last_order_sl=request.vars.req_sl
    
   
        
    
    
    item_query=f"""
    SELECT id, name FROM SM_ITEM WHERE cid='{c_id}'
    """
    item_data=db.executesql(item_query,as_dict=True)
    
    
        
    return dict(item_data=item_data,page=0,last_order_sl=last_order_sl)


def save_order():
    response.title='New Order'
    from datetime import datetime
    c_id=session.cid
    user_name=session.name
    
    order_datetime=date_fixed
    order_date=date_fixed.strftime("%Y-%m-%d")
     
    save_btn=request.vars.save
    single_save=request.vars.single_save
    cancel_order=request.vars.cancel_order
    submit_order=request.vars.submit_order

    update_btn=request.vars.update_btn
    delete_btn=request.vars.delete_btn
    
    save_btn=request.vars.save
    
    last_order_sl=request.vars.req_sl
    # return last_order_sl
    
    
    if str(request.vars.Name)=="none" or str(request.vars.Name)=="None" or str(request.vars.Name)==None:
        client_name = session.client_name
    else:
        client_name=request.vars.Name   
    if str(request.vars.mobile)=="none" or str(request.vars.mobile)=="None" or str(request.vars.mobile)==None:
        mobile = session.mobile
    else:
        mobile=request.vars.mobile   
    if str(request.vars.address)=="none" or str(request.vars.address)=="None" or str(request.vars.address)==None:
        address = session.address
    else:
        address=request.vars.address   

        
    # mobile=request.vars.mobile
    # address=request.vars.address
    # session.Name=client_name
    # session.mobile=mobile
    # session.address=address
    # print(session)
    
    item_query=f"""SELECT * FROM SM_ITEM WHERE cid='{c_id}'"""
    
    item_data=db.executesql(item_query,as_dict=True)
    
    if save_btn:
        if request.vars:
            head_flag=False
            for item in item_data:
                name=item['name']
                item_id=item['item_id']
                stock_quantity=item['stock_quantity']
                price=item['price']
                vat=item['vat_amt']
                quantity = request.vars[f"quantity_{item['name']}"]
                # return stock_quantity,quantity,vat
                # total_amt = float((float(price)+float(vat))*int(quantity))
                
                if quantity:
                    
                    # insert temp table
                    
                    insert_temp= f"INSERT INTO `sm_order_temp`(`item_id`,`sl`, `name`, `order_qty`, `stock_quantity`, `price`, `vat`) VALUES ('{item_id}','{last_order_sl}','{name}','{quantity}','{stock_quantity}','{price}','{vat}')"

                    # return insert_temp
                    inserted=db.executesql(insert_temp)
                    
                    
                    # insert order table
                    status="Draft"
                    insert_order= f""" 
                    insert into sm_order (cid,item_id,item_name,sl,client_name,moblie,level3_name, quantity,price,item_vat,status,order_date,order_datetime,created_on,created_by) 
                    values ('{c_id}','{item_id}','{name}','{last_order_sl}','{client_name}','{mobile}','{address}','{quantity}','{price}','{vat}','{status}','{order_date}','{order_datetime}','{order_datetime}','{user_name}')
                    """
                    # return insert_order
                    inserted=db.executesql(insert_order)
                    
                    head_flag=True
            if head_flag==True:   
                status="Draft"
                insert= f""" 
                insert into sm_order_head (cid,sl,client_name,mobile_no,level3_name,status,order_date,created_on,created_by) 
                values ('{c_id}','{last_order_sl}','{client_name}','{mobile}','{address}','{status}','{order_date}','{order_datetime}','{user_name}')
                """
                # return insert
                inserted=db.executesql(insert)
    
    
    if single_save:
        sl = request.vars.req_sl
        item_id=request.vars.record_id
        item_name=request.vars.item_name_input
        quantity=request.vars.qty_input
        # return sl
        check_query=f"SELECT * FROM SM_ITEM WHERE cid='{c_id}' and name='{item_name}' limit 1"
     
        check=db.executesql(check_query,as_dict=True)
        if len(check)>0:
            item_name=check[0]['name']
            price=check[0]['price']
            vat_amt=check[0]['vat_amt']
            stock_quantity=check[0]['stock_quantity']

            # check duplicate
            dup=f"SELECT * FROM sm_order_temp WHERE name='{item_name}' and sl='{sl}' limit 1"
            duplicate=db.executesql(dup,as_dict=True)
            
            if len(duplicate)>0:
                response.flash="Duplicate item found, Item is already ordered please update!"
            else:
                insert_temp= f""" 
                insert into sm_order_temp (item_id,sl,name,order_qty,stock_quantity,price,vat) 
                values ('{item_id}','{sl}','{item_name}','{quantity}','{stock_quantity}','{price}','{vat_amt}')
                """
                inserted=db.executesql(insert_temp)
                
                # insert order table
                status="Draft"
                insert_order= f""" 
                insert into sm_order (cid,item_id,item_name,sl,client_name,moblie,level3_name, quantity,price,item_vat,status,order_date,order_datetime,created_on,created_by) 
                values ('{c_id}','{item_id}','{item_name}','{last_order_sl}','{client_name}','{mobile}','{address}','{quantity}','{price}','{vat_amt}','{status}','{order_date}','{order_datetime}','{order_datetime}','{user_name}')
                """
                # return insert
                inserted=db.executesql(insert_order)
        
            # for item in item_data:
            #         name=item['name']
            #         item_id=item['item_id']
            #         stock_quantity=item['stock_quantity']
            #         price=item['price']
            #         vat=item['vat_amt']
                    
                    # if name==item_name:
                    #     # check duplicate
                    #     dup=f"SELECT * FROM sm_order_temp WHERE name='{item_name}' and sl='{sl}' limit 1"
                    #     duplicate=db.executesql(dup,as_dict=True)
                        
                    #     if len(duplicate)>0:
                    #         response.flash="Duplicate item found, Item is already ordered!"
                    #     else:
                    #         insert_temp= f""" 
                    #         insert into sm_order_temp (item_id,sl,name,order_qty,stock_quantity,price,vat) 
                    #         values ('{item_id}','{sl}','{name}','{quantity}','{stock_quantity}','{price}','{vat}')
                    #         """
                    #         # return insert
                    #         inserted=db.executesql(insert_temp)
                            
                    #         # insert order table
                    #         status="Draft"
                    #         insert_order= f""" 
                    #         insert into sm_order (cid,item_id,item_name,sl,client_name,moblie,level3_name, quantity,price,item_vat,status,order_date,order_datetime,created_on,created_by) 
                    #         values ('{c_id}','{item_id}','{name}','{last_order_sl}','{client_name}','{mobile}','{address}','{quantity}','{price}','{vat}','{status}','{order_date}','{order_datetime}','{order_datetime}','{user_name}')
                    #         """
                    #         # return insert
                    #         inserted=db.executesql(insert_order)
        else:
            response.flash="Item not found!"

    if submit_order:
        status = "Submitted"
        update_qty = f"UPDATE sm_item i JOIN sm_order_temp t ON i.name = t.name SET i.stock_quantity = i.stock_quantity - t.order_qty;"
        db.executesql(update_qty)
        update_order = f"""
            UPDATE sm_order SET status='{status}' WHERE cid='{c_id}' AND sl='{last_order_sl}'
        """
        db.executesql(update_order)
        
        update_head = f"""
            UPDATE sm_order_head SET status='{status}' WHERE cid='{c_id}' AND sl='{last_order_sl}'
        """
        db.executesql(update_head)

        
        # Clean temp table
        delete_temp = """
            DELETE FROM sm_order_temp WHERE 1
        """
        db.executesql(delete_temp)
        
        redirect(URL('order','order'))
    # return btn_update
   
    if cancel_order:
        status = "Cancel"
        update_order = f"""
            UPDATE sm_order SET status='{status}' WHERE cid='{c_id}' AND sl='{last_order_sl}'
        """
        db.executesql(update_order)
        
        update_head = f"""
            UPDATE sm_order_head SET status='{status}' WHERE cid='{c_id}' AND sl='{last_order_sl}'
        """
        db.executesql(update_head)
        
        # Clean temp table
        delete_temp = """
            DELETE FROM sm_order_temp WHERE 1
        """
        db.executesql(delete_temp)
        redirect(URL('order','order'))

    if update_btn:
        order_qty=request.vars.qty
        record_id=request.vars.record_id
        record_name=request.vars.record_name
        record_sl=request.vars.req_sl
        # return f"{order_qty} {record_id}"
        update_query=f"update sm_order_temp set order_qty='{order_qty}' where id='{record_id}'"
        db.executesql(update_query)
        update_order_query=f"update sm_order set quantity='{order_qty}' where item_name='{record_name}' and sl='{record_sl}' limit 1"
        db.executesql(update_order_query)
        session.flash = "Updated Successfully!"
        redirect(URL('web_order','save_order',vars=dict(req_sl=last_order_sl)))
    
    if delete_btn:
        record_id=request.vars.record_id
        record_name=request.vars.record_name
        record_sl=request.vars.req_sl
        # return record_name,record_sl
        check_rec_exist_sql = f" select * from sm_order_temp  where id='{record_id}'"
        check_rec_exist = db.executesql(check_rec_exist_sql,as_dict=True)
        check_item_exist_sql = f" select * from sm_order_temp  where id='{record_id}'"
        check_item_exist = db.executesql(check_item_exist_sql,as_dict=True)
        if len(check_rec_exist)==0:
            response.flash = "item does not exists"
        else:
            update_query=f"delete from sm_order_temp  where id='{record_id}' limit 1"
            db.executesql(update_query)

        if len(check_item_exist)==0:
            response.flash = "item does not exists"
        else:
            update_query=f"delete from sm_order  where item_name='{record_name}' and sl='{record_sl}' limit 1"
            db.executesql(update_query)

    # item_query=f"SELECT id, name,order_qty,stock_quantity,price,vat FROM sm_order_temp WHERE sl={last_order_sl} "
    item_query=f"SELECT t.id, t.name, t.order_qty, i.stock_quantity, i.price, i.vat_amt FROM sm_order_temp t, sm_item i WHERE t.name = i.name and t.sl ={last_order_sl} GROUP by i.name;"
    # return item_query
    temp_data=db.executesql(item_query,as_dict=True)
    order_head_query=f"SELECT id, client_name,level3_name,mobile_no FROM sm_order_head WHERE cid='{c_id}' and sl='{last_order_sl}' order by id desc limit 1;"
    # return order_head_query
    order_head=db.executesql(order_head_query,as_dict=True)
    if len(order_head)>0:
        client_name = order_head[0]['client_name']
        mobile = order_head[0]['mobile_no']
        address = order_head[0]['level3_name']
    # return client_name, mobile,address
    
    return dict(
        item_data=item_data,page=0,temp_data=temp_data,last_order_sl=last_order_sl,
        client_name=client_name,mobile=mobile,address=address)
    

def update_delete_temp_order():
    order_qty=request.vars.order_qty
    record_id=request.vars.record_id
    # return "a"
    return order_qty, record_id
    update_btn=request.vars.update_btn
    delete_btn=request.vars.delete_btn
    if update_btn:
        order_qty=request.vars.order_qty
        record_id=request.vars.record_id
        return order_qty, record_id
        
        update_query=f"""
            update sm_order_temp set order_qty='{order_qty}' where id='{record_id}'
        """
        db.executesql(update_query)

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


def get_item_name():
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


# def update_order():
#     cid= session.cid
#     item_name = request.args(0)
#     # return item_id
#     check_query = f"SELECT * FROM sm_item WHERE cid = '{cid}' and name = '{item_name}' order by name limit 1"
#     check_sql=db.executesql(check_query, as_dict = True)
#     if len(check_sql)>0:
#         id = check_sql['']
#         name = check_sql['name']
#         qty = check_sql['stock_quantity']

#     # update_query
    
#     return locals()