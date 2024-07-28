def item():
   
    
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    
    session.item_id_filter = ''
    session.ym_date_filter=''
    
    btn_filter_item=request.vars.btn_filter_item
    btn_all = request.vars.btn_all
    item_id_filter = request.vars.item_id_filter


    condition = ''
    reqPage = len(request.args)
    # return c_id
    
    cid=session.cid
    user_id=session.user_id
   
    
    submit=request.vars.submit
    if submit:
        
        item_id=request.vars.item_id
        item_name=request.vars.item_name
        qty =request.vars.quantity
        tp =request.vars.tp_amount
        vat=request.vars.vat_amount
        
        # return status
        if item_id=='' or item_id==None or item_id=='None':
            response.flash = 'Please Enter Item ID'
        elif item_name=='' or item_name==None or item_name=='None':
            response.flash = 'Please Enter Item Name'
        elif qty=='' or qty==None or qty=='None':
            response.flash = 'Please Enter Item Quantity'
        elif int(qty)<=0:
            response.flash = 'Item Quantity must be bigger than Zero'
        elif tp=='' or tp==None or tp=='None':
            response.flash = 'Please Enter TP AMOUNT'
        elif vat=='' or vat==None or vat=='None':
            response.flash = 'Please Enter VAT AMOUNT'
        else:
            
            check_item_sql = "select * from sm_item where cid='"+str(cid)+"'and item_id='"+str(item_id)+"' and name='"+str(item_name)+"' limit 1;"
            # return check_item_sql
            check_item = db.executesql(check_item_sql, as_dict=True)
            # return check_item
            if len(check_item)>0:
                stock_quantity=check_item[0]['stock_quantity']
                stock_quantity=stock_quantity+qty
                update_query =f""" update sm_item set stock_quantity='{stock_quantity}' 
                where cid='{cid}' and item_id='{item_id}' and item_name='{item_name}' limit 1 """
                db.executesql(update_query)
                response.flash= 'Item is already exist ! Successfully Update Qty!'
                
            else:
                                
                insertitem_sql = f"""
                    INSERT INTO sm_item 
                    (cid,item_id,name,stock_quantity,price, vat_amt ,updated_by) 
                    VALUES ('{cid}', '{item_id}', '{item_name}', '{qty}', '{tp}', '{vat}', '{user_id}')"""
                insertitem = db.executesql(insertitem_sql)
                response.flash= 'Successfully saved!'
                
                session.item_id_filter = ''
                session.ym_date_filter=''
    
    # --------paging
    session.items_per_page=20
    if reqPage:
        page=int(request.args[0])
    else:
        page=0
    items_per_page=session.items_per_page
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    # --------end paging
    
    
  
    
    
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


def item_edit():
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    # return 'flhj'
    id =request.args(0)
    
    
    cid=session.cid
    user_id=session.user_id
    update_btn = request.vars.update_btn
    delete_btn = request.vars.delete_btn

    select_item_record_sql = f"SELECT * FROM sm_item WHERE id ='"+str(id)+"' GROUP BY id LIMIT 1;"
    # return select_item_record_sql
    selected_item_record = db.executesql(select_item_record_sql, as_dict = True)
    # return 11

    # if len(selected_ret_record) != 0 :
    for i in range(len(selected_item_record)):
        records_ov_dict = selected_item_record[i]
       
        item_id=str(records_ov_dict["item_id"])
        item_name=str(records_ov_dict["name"])
        
        tp=str(records_ov_dict["price"])
        qty=str(records_ov_dict["stock_quantity"])
        vat=str(records_ov_dict["vat_amt"])
       
        
    
    if update_btn:
        
        
        qty =request.vars.quantity
        tp=request.vars.tp_amount
        vat=request.vars.vat_amt
        # return  price_up 
    
        if qty=='' or qty==None or qty=='None':
            response.flash = 'Please Enter Item Quantity'
        elif int(float(qty))<=0:
            response.flash = 'Item Quantity must be bigger than Zero'
        elif tp=='' or tp==None or tp=='None':
            response.flash = 'Please Enter TP Amount'
        elif vat=='' or vat==None or vat=='None':
            response.flash = 'Please Enter Vat Amount'
        else:                   
            update_sql = f"UPDATE sm_item SET stock_quantity='"+str(qty)+"', price = '"+str(tp)+"',vat_amt = '"+str(vat)+"',updated_by = '"+str(user_id)+"' WHERE id ='"+str(id)+"' LIMIT 1;"
            # return update_sql
            up_date = db.executesql(update_sql)

            session.flash = 'Update Successfully!'

            redirect(URL('item','item'))
            
            
    if delete_btn:
        delete_sql = f"DELETE FROM sm_item WHERE id='{id}' LIMIT 1;"
        delete = db.executesql(delete_sql)

        session.flash = 'Deleted Successfully!'

        redirect(URL('item','item'))
            
    return dict(id=id,item_id=item_id,item_name=item_name,qty=qty,vat_amt=vat, tp_amount=tp)
    



def item_batch_upload():
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    response.title = 'Item Batch Upload'
    session.item_id_filter = ''
    session.ym_date_filter=''
    user_id=session.user_id
    
    c_id = session.cid
    btn_upload = request.vars.btn_upload
    count_inserted = 0
    count_error = 0
    error_str = ''
    total_row = 0
    slNo = 0
    # return slNo
    if btn_upload == 'Upload':
        excel_data = str(request.vars.excel_data)
        error_list = []
        row_list = excel_data.split('\n')
        total_row = len(row_list)
        # create list
        if total_row>=500:
            error_str="Maximum number of rows exceeded. Please insert less than 100 rows"
        else:
            for i in range(total_row):
                
                row_data = row_list[i]
                coloum_list = row_data.split('\t')

                if len(coloum_list) != 2:
                    error_data = row_data + '(2 columns need in a row)\n'
                    error_str = error_str + error_data
                    count_error += 1
                    continue
                else:
                    item_name = str(coloum_list[0]).strip().upper()
                    qty = str(coloum_list[1]).strip()
                   

                    
                    # return status_excel

                    if (item_name=='' or item_name== 'None') or (qty=='' or qty == 'None') :
                        error_data=row_data+'(Required all value)\n'
                        error_str=error_str+error_data
                        count_error+=1
                        continue 
                    
                    
                    else:
                        
                        existCheckRows= " SELECT * FROM sm_item WHERE cid='"+str(c_id)+"' and name = '"+item_name+"';"
                        # return existCheckRows
                        existCheck = db.executesql(existCheckRows, as_dict=True)
                        # return existCheck

                        if len(existCheck) > 0:
                            # update item table qty
                            stock_quantity=existCheck[0]['stock_quantity']
                            stock_quantity=int(stock_quantity)+int(qty)
                            update_query =f""" update sm_item set stock_quantity='{stock_quantity}' 
                            where cid='{c_id}'and name='{item_name}' limit 1 """
                            db.executesql(update_query)
                            count_inserted+=1 
                            
                        else:
                            try:
                                insertitem_sql = f"""
                                    INSERT INTO sm_item 
                                    (cid,name, stock_quantity,created_by ) 
                                    VALUES ('{c_id}', '{item_name}','{qty}','{user_id}');
                                """     
                                insertitem = db.executesql(insertitem_sql)  
                            
                                count_inserted+=1  
                                    
                            except Exception as e:
                                error_str = 'Please do not insert special charachter.'
                                # return error_str


        if error_str == '':
            error_str = 'No error'

    return dict(count_inserted=count_inserted, count_error=count_error, error_str=error_str, total_row=total_row)


def items_download():
    if (session.cid=='' or session.cid==None):
        redirect (URL('default','index'))
    c_id = session.cid
    condition = ''
    condition = session.condition

    download_sql = "select * from sm_item where cid = '"+c_id+"' "+condition+";"
    download_records = db.executesql(download_sql, as_dict=True)
    
    myString = 'Item List\n\n'
    myString += 'item_id,item_name,Stock Quantity,TP Amount,Vat Amount\n'
    total=0
    attTime = ''
    totalCount = 0
    for i in range(len( download_records)):
        recordsStr =  download_records[i]
        item_id=str(recordsStr["item_id"])
        name=str(recordsStr["name"])
        qty=str(recordsStr["stock_quantity"])
        tp=str(recordsStr["price"])
        vat_amt=str(recordsStr["vat_amt"])
        
        


        myString += str(item_id) + ',' + str(name) + ','  + str(qty) + ',' + str(tp) + ',' + str(vat_amt) +'\n'

    # Save as csv
    import gluon.contenttype
    response.headers['Content-Type'] = gluon.contenttype.contenttype('.csv')
    response.headers['Content-disposition'] = 'attachment; filename=download_Item.csv'
    return str(myString) 




def get_all_item_list():
    retStr = ''
    cid = session.cid
    # return cid
    # rows = db(db.sm_item.cid == cid).select(db.sm_item.item_id, db.sm_item.name, orderby=db.sm_item.name)
    
    sql_query = f"SELECT item_id,name from sm_item where cid = '{cid}' order by name"

    # print('get_all_item_list: sql_query: ', sql_query)
    rows = db.executesql(sql_query, as_dict = True)

    # print('rows: ',len(rows))

    for idx in range(len(rows)):
        # item_id = str(row.item_id)
        # name = str(row.name).replace('|', ' ').replace(',', ' ')
        item_id = rows[idx]['item_id']
        name = rows[idx]['name']
        # print(item_id, ' :: ', name)

        if retStr == '':
            retStr = item_id + '|' + name
        else:
            retStr += ',' + item_id + '|' + name

    return retStr