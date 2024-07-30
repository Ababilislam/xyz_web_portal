def new_web_order_entry():  
    response.title='New Order'
    from datetime import datetime
    c_id=session.cid
     
    save_btn=request.vars.save
    
   
        
        
    
    item_query=f"""
    SELECT id, name FROM SM_ITEM WHERE cid='{c_id}'
    """
    item_data=db.executesql(item_query,as_dict=True)
    
    if save_btn:
        
        if request.vars:
            
            for item in item_data:
                name=item['name']
                quantity = request.vars[f"quantity_{item['id']}"]
                
                if quantity:
                    
                    insert= f""" insert into sm_order_temp1 (name,qty) values ('{name}','{quantity}')"""
                    
                    inserted=db.executesql(insert)
        
    return dict(item_data=item_data,page=0)


def save_order():
    response.title='New Order'
    from datetime import datetime
    c_id=session.cid
     
    save_btn=request.vars.save
    
   
        
        
    
    item_query=f"""
    SELECT id, name FROM SM_ITEM WHERE cid='{c_id}'
    """
    item_data=db.executesql(item_query,as_dict=True)
    
    if save_btn:
        
        if request.vars:
            
            for item in item_data:
                name=item['name']
                quantity = request.vars[f"quantity_{item['id']}"]
                
                if quantity:
                    
                    insert= f""" insert into sm_order_temp1 (name,qty) values ('{name}','{quantity}')"""
                    
                    inserted=db.executesql(insert)
        
    item_query=f"""
    SELECT id, name,qty FROM sm_order_temp1 WHERE 1
    """
    temp_data=db.executesql(item_query,as_dict=True)
    
    
    
    return dict(item_data=item_data,page=0,temp_data=temp_data)
    
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