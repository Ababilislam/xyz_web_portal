# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import random
from random import randint
from operator import itemgetter

#-------------------------------------- set_transaction_balance
#cid<fdfd>tx_type<fdfd>sl<fdfd>datetime<fdfd>reference<fdfd>1st account with prefix (cr)<fdfd>2nd account with prefix (dr)<fdfd>tx_amount
#ABC<fdfd>ISSUE<fdfd>20<fdfd>2012-07-01 12:44:20<fdfd>abc-issue-20<fdfd>HO<fdfd>02<fdfd>1000

# number to currency
def number_to_words(n):
    # Define lists for various number names
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
            "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]

    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    thousands = ["", "Thousand", "Million", "Billion"]

    if n == 0:
        return "Zero"

    def recursive_words(number, idx):
        if number == 0:
            return ""
        elif number < 20:
            return ones[number] + " "
        elif number < 100:
            return tens[number // 10] + " " + recursive_words(number % 10, 0)
        else:
            return ones[number // 100] + " Hundred " + recursive_words(number % 100, 0)

    words = ""
    idx = 0
    while n > 0:
        if n % 1000 != 0:
            words = recursive_words(n % 1000, idx) + thousands[idx] + " " + words
        n //= 1000
        idx += 1

    return words.strip()

# ==========================




def set_balance_transaction(strData):
    myStr=strData    
    separator='<fdfd>'
    myList=myStr.split(separator,myStr.count(separator))
    
    returnStr='True<sep>success'
    errorStr=''
    test=''
    
    if len(myList)!=8:
        returnStr='False<sep>internal process error:invalid function value'
    else:
        try:
            cid=myList[0]
            txType=myList[1]
            typeSl=myList[2]
            txDate=date_fixed   #myList[3]            
            typeRef=myList[4]
            txAccount=myList[5]
            oppAccount=myList[6]
            txAmount=myList[7]
            
            txFirstID=str(txType)+'-'+str(txAccount)+'-'+str(typeSl)
            txSecondID=str(txType)+'-'+str(oppAccount)+'-'+str(typeSl)
            
            dictList=[]
            txClosingBal=0.0
            oppClosingBal=0.0
            
            #------------------------ get previous closing balance row_flag='1'
            txPreClosing=0.0
            oppositePreClosing=0.0
            txRows=db((db.sm_transaction.cid==cid) & (db.sm_transaction.tx_account==txAccount)& (db.sm_transaction.opposite_account==oppAccount)& (db.sm_transaction.row_flag=='0')).select(db.sm_transaction.id,db.sm_transaction.tx_closing_balance,orderby=~db.sm_transaction.tx_date,limitby=(0,1))
            if txRows:
                txPreClosing=float(txRows[0].tx_closing_balance) 
                txPreClosing=round(txPreClosing,2)
            oppositeRows=db((db.sm_transaction.cid==cid) & (db.sm_transaction.tx_account==oppAccount)& (db.sm_transaction.opposite_account==txAccount)& (db.sm_transaction.row_flag=='0')).select(db.sm_transaction.id,db.sm_transaction.tx_closing_balance,orderby=~db.sm_transaction.tx_date,limitby=(0,1))
            if oppositeRows:
                oppositePreClosing=float(oppositeRows[0].tx_closing_balance)
                oppositePreClosing=round(oppositePreClosing,2)
                
            crAmount=round(float(txAmount)*(-1),2)
            drAmount=round(float(txAmount),2)
            
            txClosingBal=round(txPreClosing+crAmount,2)
            oppClosingBal=round(oppositePreClosing+drAmount,2)
            
            #------------------- tx description
            txDescription=''
            oppDescription=''
            
            primarySalesType='P'
            secondarySalesType='S'
            
            if txType=='ISSUE':
                txDescription=str(txAccount)+' Issued to '+str(oppAccount)                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':txType,'sales_type':primarySalesType,'reference':typeRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                dictList.append(txDict)
            
            elif txType=='RECEIVE':
                oppDescription=str(oppAccount)+' Received from '+str(txAccount) 
                          
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':txType,'sales_type':primarySalesType,'reference':typeRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(oppDict)
            
            elif txType=='ISSUERECEIVE':
                #------------- used for preview voucher ;if list=1 then import/factory/opening elseif list=2 both are not equal then issue and receive but both are equal import/factory/opening return,
                issueRef=''
                receiveRef=''
                tx_type_issue='ISSUE'
                tx_type_receive='RECEIVE'                
                typeRefList=typeRef.split(':',typeRef.count(':'))                
                if len(typeRefList)==2:
                    issueRef=typeRefList[0]
                    receiveRef=typeRefList[1]                    
                    
                    if str(issueRef)==str(receiveRef):
                        issueRef=typeRefList[0]
                        receiveRef=typeRefList[0]                    
                        tx_type_issue='ISSUE'
                        tx_type_receive='EXPORT'
                else:
                    issueRef=typeRef
                    receiveRef=typeRef                    
                    tx_type_issue='IMPORT'
                    tx_type_receive='RECEIVE'
                #-----------
                
                txDescription=str(txAccount)+' Issued to '+str(oppAccount)   
                oppDescription=str(oppAccount)+' Received from '+str(txAccount)
                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':tx_type_issue,'sales_type':primarySalesType,'reference':issueRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':tx_type_receive,'sales_type':primarySalesType,'reference':receiveRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(txDict)
                dictList.append(oppDict)
            
            elif txType=='DAMAGE':
                txDescription=str(txAccount)+' Damaged to '+str(oppAccount) 
                oppDescription=str(oppAccount)+' Damaged-Received from '+str(txAccount)
                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':txType,'sales_type':primarySalesType,'reference':typeRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':txType,'sales_type':primarySalesType,'reference':typeRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(txDict)
                dictList.append(oppDict)
            
            
            elif txType=='DELIVERY':
                txDescription=str(txAccount)+' Delivered to '+str(oppAccount) 
                oppDescription=str(oppAccount)+' Delivery-Received from '+str(txAccount)
                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(txDict)
                dictList.append(oppDict)
            
            elif txType=='RETURN':
                txDescription=str(txAccount)+' Returned to '+str(oppAccount) 
                oppDescription=str(oppAccount)+' Return-Received from '+str(txAccount)
                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(txDict)
                dictList.append(oppDict)
                
            elif txType=='RETURNCANCEL':
                txDescription=str(txAccount)+' Returned-Cancelled to '+str(oppAccount) 
                oppDescription=str(oppAccount)+' Return-Cancelled from '+str(txAccount)
                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(txDict)
                dictList.append(oppDict)
                
            elif txType=='DPTPAYMENT':
                txDescription=str(txAccount)+' Payment to '+str(oppAccount) 
                oppDescription=str(oppAccount)+' Payment-Received from '+str(txAccount)
                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':txType,'sales_type':primarySalesType,'reference':typeRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':txType,'sales_type':primarySalesType,'reference':typeRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(txDict)
                dictList.append(oppDict)
            
            elif txType=='CLTPAYMENT':
                txDescription=str(txAccount)+' Payment to '+str(oppAccount) 
                oppDescription=str(oppAccount)+' Payment-Received from '+str(txAccount)
                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(txDict)
                dictList.append(oppDict)
            
            elif txType=='PAYMENTCLT':
                txDescription=str(txAccount)+' Payment to '+str(oppAccount) 
                oppDescription=str(oppAccount)+' Payment-Received from '+str(txAccount)
                
                txDict={'cid':cid,'txid':txFirstID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':txAccount,'opposite_account':oppAccount,'tx_op_balance':txPreClosing,'tx_amount':crAmount,'tx_closing_balance':txClosingBal,'tx_des':txDescription}
                oppDict={'cid':cid,'txid':txSecondID,'tx_date':txDate,'tx_type':txType,'sales_type':secondarySalesType,'reference':typeRef,'tx_account':oppAccount,'opposite_account':txAccount,'tx_op_balance':oppositePreClosing,'tx_amount':drAmount,'tx_closing_balance':oppClosingBal,'tx_des':oppDescription}
                dictList.append(txDict)
                dictList.append(oppDict)
                
            #---------------
            if len(dictList)>0:
                insertRes=db.sm_transaction.bulk_insert(dictList)
                
                if txType=='ISSUE':
                    if txRows:
                        txRows[0].update_record(row_flag='1')
                    
                elif txType=='RECEIVE':
                    if oppositeRows:
                        oppositeRows[0].update_record(row_flag='1')
                else:
                    if txRows:
                        txRows[0].update_record(row_flag='1')
                    if oppositeRows:
                        oppositeRows[0].update_record(row_flag='1')
                
        # ------------
        except:
            db.rollback()
            returnStr='False<sep>process error during transaction %s'%(test)
            return returnStr
        
        
    return returnStr


def getStrSl():
    slStr=''
    #-------------- get random number
    randNum=random.randint(100, 999)        
    #date_fixed = 2012-07-01 11:48:10.000012
    yy=str(date_fixed)[2:4]
    mm=str(date_fixed)[5:7]  
    dd=str(date_fixed)[8:10]
    hh=str(date_fixed)[11:13] 
    mn=str(date_fixed)[14:16] 
    ss=str(date_fixed)[17:19] 
    ms=str(date_fixed)[20:26]        
    slStr=yy+mm+dd+'.'+hh+mn+ss+'.'+ms+'.'+str(randNum)
    
    return slStr


##---------------------Encript data

def get_encript(mystr):
    randNumberLength=2
    add_with_ascii=333
    add_eightbit_string='34523434'
    ascii_for_string_full=''
    
    str_single_char=list(mystr)
    
    total=len(str_single_char)
    
    for i in range(total):
        str_single= ord(str_single_char[i])+add_with_ascii
        ascii_for_string_full=ascii_for_string_full+str(str_single)
    
    strlength=len(ascii_for_string_full)

    randNumber = random.randint(1, 99)

    if (randNumber > strlength):
        randNumber = random.randint(1, strlength-1)
    
    if(randNumber<10):
        randNumber='0'+str(randNumber)
   
    firstpart=ascii_for_string_full[0:int(randNumber)]
    secondpart=ascii_for_string_full[int(randNumber):]    
    encripted=str(randNumber)+firstpart+add_eightbit_string+secondpart    
    
    return encripted


#-------------------------------- Decript data
def get_decript(mystr):
    
    digit_flag=mystr.isdigit()
    string_for_ascii_full=''
    
    if digit_flag:
        add_with_ascii=333
        add_eightbit_string='34523434'
        randNumber=int(mystr[0:2])
        ascii_with_eightbit_string=mystr[2:]
        
        firstPart=ascii_with_eightbit_string[0:randNumber]        
        secondPart_withstring=ascii_with_eightbit_string[randNumber:]
        
        eight_bit_string=secondPart_withstring[0:8]

        if(eight_bit_string==add_eightbit_string):

            secondPart=secondPart_withstring[8:]
            mainString=str(firstPart)+str(secondPart)
        
            
            ascii_single=[]
            chval=''
            for ch in mainString:
                chval+=ch
                if len(chval)==3:
                    ascii_single.append(chval)
                    chval=''
                else:
                    continue
                
            total=len(ascii_single)
        
            for i in range(total):
                
                single_ascii= int(ascii_single[i])-add_with_ascii
                single_ascii=unichr(single_ascii)
                string_for_ascii_full=string_for_ascii_full+single_ascii

            return string_for_ascii_full

        else:
            return string_for_ascii_full
      
    else:
        return string_for_ascii_full

#-------------------------------- role access check
def check_role(task_id):
    t_id=task_id
    
    is_valid_role=False
    
    task_listStr=session.task_listStr
    return task_listStr
    taskList=str(task_listStr).split(',')
    for i in range(len(taskList)):
        taskid=taskList[i]
        if taskid==t_id:
            is_valid_role=True
            break
        else:
            continue
    
    return is_valid_role

#-------------------------------
def get_mydate(gmt_time):
    import datetime;
    if gmt_time==None:
        gmt_time=0
    
    my_date =datetime.datetime.now()+ datetime.timedelta(hours=gmt_time);
    session.my_date=my_date
    return my_date;


#======================
def check_special_char(strData):
    strData=strData.replace("@", " ")
    strData=strData.replace("<", " ")
    strData=strData.replace(">", " ")
    strData=strData.replace("(", " ")
    strData=strData.replace(")", " ")
    strData=strData.replace("{", " ")
    strData=strData.replace("}", " ")
    strData=strData.replace("[", " ")
    strData=strData.replace("]", " ")
    strData=strData.replace(",", " ")
    strData=strData.replace("`", " ")
    strData=strData.replace("'", " ")
    strData=strData.replace('"', ' ')
    strData=strData.replace("*", " ")
    strData=strData.replace("#", " ")
    strData=strData.replace(";", " ")
    strData=strData.replace("-", " ")
    strData=strData.replace("/", " ")    
    return strData
    
def check_special_char_id(strData):
    strData=strData.replace("@", "")
    strData=strData.replace("<", "")
    strData=strData.replace(">", "")
    strData=strData.replace("(", "")
    strData=strData.replace(")", "")
    strData=strData.replace("{", "")
    strData=strData.replace("}", "")
    strData=strData.replace("[", "")
    strData=strData.replace("]", "")
    strData=strData.replace(",", "")
    strData=strData.replace("`", "")
    strData=strData.replace("'", "")
    strData=strData.replace('"', '')
    strData=strData.replace("*", "")
    strData=strData.replace("#", "")
    strData=strData.replace(";", "")  
    strData=strData.replace(" ", "")
    strData=strData.replace("/", "")
    return strData
    
#***** new invoice with promotion and credit limit
def get_order_to_delivery_detail_rules(cid,depot_id,order_sl,clientId,orderDate):
    c_id=cid
    depot_id=depot_id
    sl=order_sl
    client_id=clientId
    orderDate=orderDate
    
    #========================-get settings flag
    invoiceRulesFlag=False
    
    compSttRows=db((db.sm_settings.cid==c_id)&(db.sm_settings.s_key=='INVOICE_RULES')&(db.sm_settings.s_value=='YES')).select(db.sm_settings.cid,limitby=(0,1))
    if compSttRows:
        invoiceRulesFlag=True
        
    #================ if invoice rules are to apply (Note: ANY or Sepcific item, at a time two rules not applicable)
    productBonusPriorityRows=''
    approvedItemRows=''    
    productBonusRows=''
    specialRateRows=''
    flatRateRows=''
    promo_ref=0 #0=No,1=Yes
    if invoiceRulesFlag==True:        
        orderHeadRow=db((db.sm_order_head.cid==c_id) & (db.sm_order_head.depot_id==depot_id) & (db.sm_order_head.sl==sl)).select(db.sm_order_head.promo_ref,limitby=(0,1))
        if orderHeadRow:
            promo_ref=orderHeadRow[0].promo_ref
            if promo_ref!=0:
                promo_ref=1
        
        approvedItemRows=db((db.sm_promo_approved_rate.cid==c_id)&(db.sm_promo_approved_rate.client_id==client_id)&(db.sm_promo_approved_rate.from_date<=orderDate)&(db.sm_promo_approved_rate.to_date>=orderDate)&(db.sm_promo_approved_rate.status=='ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date|db.sm_promo_approved_rate.product_id)
        productBonusRows=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,db.sm_promo_product_bonus.until_stock_last,db.sm_promo_product_bonus.allowed_credit_inv,db.sm_promo_product_bonus.regular_discount_apply,orderby=~db.sm_promo_product_bonus.min_qty)           # orderby min desc because same item many rules can be present
        specialRateRows=db((db.sm_promo_special_rate.cid==c_id)&(db.sm_promo_special_rate.from_date<=orderDate)&(db.sm_promo_special_rate.to_date>=orderDate)&(db.sm_promo_special_rate.status=='ACTIVE')).select(db.sm_promo_special_rate.product_id,db.sm_promo_special_rate.min_qty,db.sm_promo_special_rate.special_rate_tp,db.sm_promo_special_rate.special_rate_vat,db.sm_promo_special_rate.allowed_credit_inv,db.sm_promo_special_rate.regular_discount_apply,orderby=~db.sm_promo_special_rate.from_date)
        flatRateRows=db((db.sm_promo_flat_rate.cid==c_id)&(db.sm_promo_flat_rate.from_date<=orderDate)&(db.sm_promo_flat_rate.to_date>=orderDate)&(db.sm_promo_flat_rate.status=='ACTIVE')).select(db.sm_promo_flat_rate.campaign_ref,db.sm_promo_flat_rate.product_id,db.sm_promo_flat_rate.min_qty,db.sm_promo_flat_rate.flat_rate,db.sm_promo_flat_rate.allowed_credit_inv,db.sm_promo_flat_rate.regular_discount_apply,db.sm_promo_flat_rate.allow_bundle,orderby=~db.sm_promo_flat_rate.from_date)

        # common approved rate
        #approvedItemRows = db((db.sm_promo_approved_rate.cid == c_id) & (db.sm_promo_approved_rate.from_date <= orderDate) & (db.sm_promo_approved_rate.to_date >= orderDate) & (db.sm_promo_approved_rate.status == 'ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date | db.sm_promo_approved_rate.product_id)

    #----------- get delivery max sl from depot
    maxSl=1
    records=db((db.sm_depot.cid==c_id) & (db.sm_depot.depot_id==depot_id)).select(db.sm_depot.id,db.sm_depot.del_sl,limitby=(0,1))
    if records:
        dsl=records[0].del_sl
        maxSl=int(dsl)+1
    
    #--- sl update in depot
    records[0].update_record(del_sl=maxSl)
    
    records=''
    #---------------   order detail records
    depot_name=''    
    client_name=''
    rep_id=''
    rep_name=''
    area_id=''
    area_name=''
    order_datetime=''
    payment_mode=''
    req_note=''
    ym_date=''
    req_delivery_date=''
    
    #----------------
    headList=[]                                               
    detailDict={}
    detailList=[]                            
    headFlag=False
    
    totalAmountTP=0
    totalAmountVat=0
    discount=0
    sp_discount=0
    discount_precent=0
    
    #order details loop      
    orderRecords=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)).select(db.sm_tp_rules_temp_process.ALL,limitby=(0,1))
    if orderRecords:
        depot_name=orderRecords[0].depot_name
        store_id=orderRecords[0].store_id
        store_name=orderRecords[0].store_name
        client_id=orderRecords[0].client_id
        client_name=orderRecords[0].client_name
        clientCategory=orderRecords[0].client_cat
        rep_id=orderRecords[0].rep_id
        rep_name=orderRecords[0].rep_name
        area_id=orderRecords[0].area_id
        area_name=orderRecords[0].area_name                                
        order_datetime=orderRecords[0].order_datetime
        order_media=orderRecords[0].order_media
        delivery_date=orderRecords[0].delivery_date
        payment_mode=orderRecords[0].payment_mode
        req_note=orderRecords[0].note        
        market_id=orderRecords[0].market_id
        market_name=orderRecords[0].market_name
        
        #---delivery date get from order date
        ym_date=str(delivery_date)[0:7]+'-01'
        req_delivery_date=str(delivery_date)[0:10]
        
        #head records
        headDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'store_id':store_id,'store_name':store_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,'invoice_media':order_media,'area_id':area_id,'area_name':area_name,'status':'Submitted','ym_date':ym_date,'promo_ref':promo_ref}
        headList.append(headDict)
        
        emptyBatchFlag=0
        if invoiceRulesFlag==False:
            #=========================== Rules not apply
            ordRecords=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)).select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
            for ordRecord in ordRecords:
                item_id=str(ordRecord.item_id).strip().upper()
                item_name=ordRecord.item_name
                category_id=ordRecord.category_id
                item_qty_value=int(ordRecord.quantity)
                price=float(ordRecord.price)   
                item_vat=float(ordRecord.item_vat)
                actual_tp=price
                actual_vat=item_vat
                
                item_unit=ordRecord.item_unit
                item_carton=ordRecord.item_carton
                
                #---------------
                bonus_qty=0
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)
                short_note=''
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)                        
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        stockRow.update_record(block_qty=newBlockQty)
                        
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
        
        else:
            #===================== Rules apply 
            promoFlag=0
            totalAmt=0
            
            #-------- step-0: Priority (Product Bonus)
            
            #-------- promo ref=0 (No) then aproved rate first otherwise later
            if promo_ref==0:
                #-------- step-1: Approved rate            
                ordRecords1=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)&(db.sm_tp_rules_temp_process.prio_flag==0)).select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
                for ordRec in ordRecords1:             
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)   
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton
                    actual_tp=price
                    actual_vat=item_vat
                    
                    for appItemRow in approvedItemRows:
                        product_id=str(appItemRow.product_id).strip().upper()
                        bonus_type=appItemRow.bonus_type
                        fixed_percent_rate=appItemRow.fixed_percent_rate
                        
                        if product_id==item_id:
                            short_note=''
                            newPrice=0
                            promotion_type='APPROVED'
                            bonus_applied_on_qty=0
                            circular_no=''
                            
                            if bonus_type=='Fixed':
                                newPrice=fixed_percent_rate
                                short_note='Approved Fixed Rate '+str(newPrice)+',TP '+str(price)                                
                            elif bonus_type=='Percentage':
                                newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
                                short_note='Approved '+str(fixed_percent_rate)+'% of TP '+str(price)
                                
                            #-----------
                            bonus_qty=0                        
                            totalAmountTP+=round(item_qty_value*newPrice,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)                
                            
                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                            
                            promoFlag=1                        
                            ordRec.update_record(ar_flag=1)
                            break
                            
            #-------- step-2: Product Bonus
            for prodBonusRow in productBonusRows:      
                rowid=prodBonusRow.id
                circular_number=prodBonusRow.circular_number
                min_qty=prodBonusRow.min_qty
                #until_stock_last=str(prodBonusRow.until_stock_last).strip().upper()      #for bonus
                allowed_credit_inv=str(prodBonusRow.allowed_credit_inv).strip().upper()  #for bonus
                regular_discount_apply=str(prodBonusRow.regular_discount_apply).strip().upper()  #for product ALL qty
                
                allowBonus='YES'
                if payment_mode!='CASH':
                    if allowed_credit_inv=='NO':
                        allowBonus='NO'
                        
                if allowBonus=='NO':
                    continue
                    
                pbQset=db((db.sm_promo_product_bonus_products.cid==c_id)&(db.sm_promo_product_bonus_products.refrowid==rowid)&(db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)&(db.sm_tp_rules_temp_process.prio_flag==0)&(db.sm_tp_rules_temp_process.ar_flag==0)&(db.sm_tp_rules_temp_process.pb_flag==0)&(db.sm_promo_product_bonus_products.product_id==db.sm_tp_rules_temp_process.item_id))
                totalQtyRows=pbQset.select(db.sm_tp_rules_temp_process.quantity.sum(),groupby=db.sm_tp_rules_temp_process.cid)
                
                if totalQtyRows:
                    qtyCount=totalQtyRows[0][db.sm_tp_rules_temp_process.quantity.sum()]
                    
                    if qtyCount>=min_qty:
                        
                        fullCount=int(qtyCount/min_qty)
                        
                        #===================================== for bonus calculate
                        circularStr=circular_number
                                                
                        nextQtyCount=qtyCount-min_qty*fullCount
                        
                        regularQty=0    #extra Qty
                        discountRate=0
                        
                        itemFullQty=min_qty*fullCount
                        
                        bonusDictList=[]
                        bonusDictList.append({'rowid':rowid,'fullCount':fullCount,'circularNo':circular_number})
                        
                        if nextQtyCount>0:
                            prodPromList=[]
                            totalItemRows=pbQset.select(db.sm_tp_rules_temp_process.item_id,groupby=db.sm_tp_rules_temp_process.item_id)
                            for totItemRow in totalItemRows:                            
                                prodPromList.append(totItemRow.item_id)
                                
                            productBonusRows2=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')&(db.sm_promo_product_bonus.id!=rowid)&(db.sm_promo_product_bonus.id==db.sm_promo_product_bonus_products.refrowid)&(db.sm_promo_product_bonus_products.product_id.belongs(prodPromList))).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,orderby=~db.sm_promo_product_bonus.min_qty,groupby=db.sm_promo_product_bonus.id)
                            if productBonusRows2:                            
                                for productBonusRow2 in productBonusRows2:      
                                    rowid2=productBonusRow2.id
                                    circular_number2=productBonusRow2.circular_number
                                    min_qty2=productBonusRow2.min_qty
                                    
                                    if nextQtyCount>=min_qty2:
                                        fullCount2=int(nextQtyCount/min_qty2)
                                        
                                        circularStr+=','+str(circular_number2)
                                        bonusDictList.append({'rowid':rowid2,'fullCount':fullCount2,'circularNo':circular_number2})
                                        
                                        nextQtyCount=nextQtyCount-min_qty2*fullCount2
                                        itemFullQty+=min_qty2*fullCount2
                                    else:
                                        break
                                        
                                if nextQtyCount>0:
                                    regularQty=nextQtyCount
                                    #discount apply
                            else:
                                regularQty=nextQtyCount
                                #discount apply
                        
                        #---------------- bonus stock available check
                        
                        #------ insert product and update flag
                        regularQtyDisFlag='YES'
                        bonusOnQty=itemFullQty
                        regularQtyAmt=0
                        
                        ordRecords2=pbQset.select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
                        for ordRec in ordRecords2:
                            item_id=str(ordRec.item_id).strip().upper()
                            item_name=ordRec.item_name
                            category_id=ordRec.category_id
                            item_qty_value=int(ordRec.quantity)
                            price=float(ordRec.price)   
                            item_vat=float(ordRec.item_vat)
                            item_unit=ordRec.item_unit
                            item_carton=ordRec.item_carton
                            actual_tp=price
                            actual_vat=item_vat
                            
                            #------------------
                            discount_rate=price
                            
                            specialNote=''                        
                            for spRateRow in specialRateRows:
                                product_id=str(spRateRow.product_id).strip().upper()
                                minQty=spRateRow.min_qty
                                special_rate_tp=spRateRow.special_rate_tp
                                special_rate_vat=spRateRow.special_rate_vat                                
                                allowed_credit_inv=str(spRateRow.allowed_credit_inv).strip().upper()                                
                                if product_id==item_id:
                                    allowSpecialRate='YES'
                                    if payment_mode!='CASH':
                                        if allowed_credit_inv=='NO':
                                            allowSpecialRate='NO'                        
                                            
                                    #check special rate applicable
                                    if allowSpecialRate=='NO':
                                        price=special_rate_tp
                                        item_vat=special_rate_vat
                                        regular_discount_apply='YES'                 
                                        specialNote=' with special Rate (Premium TP) and vat applied'                                    
                                        actual_tp=special_rate_tp
                                        actual_vat=special_rate_vat
                                        break
                                    else:
                                        if item_qty_value<minQty:                                    
                                            price=special_rate_tp
                                            item_vat=special_rate_vat
                                            regular_discount_apply='YES'                
                                            specialNote=' with special Rate (Premium TP) and vat applied'                                    
                                            actual_tp=special_rate_tp
                                            actual_vat=special_rate_vat
                                            break
                                        else:
                                            regular_discount_apply='NO'
                                            regularQtyDisFlag='NO'
                                            break
                            #-----------
                            bonus_qty=0
                            totalAmountTP+=round(item_qty_value*price,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)
                            short_note='Bonus apply, Circular '+str(circularStr)+str(specialNote)
                            
                            regQty=0
                            promotion_type='BONUS'                            
                            if bonusOnQty>item_qty_value:
                                bonus_applied_on_qty=item_qty_value
                                bonusOnQty=bonusOnQty-item_qty_value                                
                            else:
                                bonus_applied_on_qty=bonusOnQty
                                
                                regQty=int(item_qty_value-bonusOnQty)
                                bonusOnQty=0
                            
                            circular_no=str(circularStr)
                            
                            #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                            declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                            if not declaredItemRow:
                                discountRate=discount_rate
                                #regular rate, applied discount                                
                                if regular_discount_apply=='YES': #apply for all qty
                                    totalAmt+=round(item_qty_value*price,2)
                                    short_note+=' and regular discount'
                                else:
                                    if regularQty>0 and regQty>0:
                                        if regularQtyDisFlag=='YES':
                                            #short_note+=' and regular discount on '+str(regularQty)+' Quantity'
                                            short_note+=' and regular discount on '+str(regQty)+' Quantity'
                                            regularQtyAmt+=regQty*price
                                            
                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1           
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                            
                            promoFlag=1                            
                            ordRec.update_record(pb_flag=1)
                            
                        if regular_discount_apply!='YES': #apply for all qty
                            #new code
                            #product bonus rest qty discount apply   
                            if regularQtyDisFlag=='YES':
                                #totalAmt+=round(regularQty*discountRate,2)
                                totalAmt+=round(regularQtyAmt,2)
                                
                        #if bonusStockFlag=='YES':
                        #--------- bonus item insert                        
                        for k in range(len(bonusDictList)):
                            bonusDictData=bonusDictList[k]
                            
                            bRowid=bonusDictData['rowid']
                            bfullCount=bonusDictData['fullCount']
                            bcircularNo=bonusDictData['circularNo']
                            #end new code next use bRowid
                            
                            bonusRows=db((db.sm_promo_product_bonus_bonuses.cid==c_id)&(db.sm_promo_product_bonus_bonuses.refrowid==bRowid)&(db.sm_item.cid==c_id)&(db.sm_item.item_id==db.sm_promo_product_bonus_bonuses.bonus_product_id)).select(db.sm_promo_product_bonus_bonuses.bonus_product_id,db.sm_item.name,db.sm_item.category_id,db.sm_item.category_id_sp,db.sm_item.unit_type,db.sm_item.item_carton,db.sm_promo_product_bonus_bonuses.bonus_qty)
                            for bonusRow in bonusRows:
                                bonus_product_id=bonusRow.sm_promo_product_bonus_bonuses.bonus_product_id
                                bonus_product_name=bonusRow.sm_item.name
                                bonus_product_category_id=bonusRow.sm_item.category_id
                                bonus_product_category_id_sp=bonusRow.sm_item.category_id_sp
                                bonus_item_qty=bonusRow.sm_promo_product_bonus_bonuses.bonus_qty
                                bonus_product_unit_type=bonusRow.sm_item.unit_type
                                bonus_product_item_carton=bonusRow.sm_item.item_carton
                                actual_tp=0
                                actual_vat=0
                                #----
                                item_id=bonus_product_id
                                item_name=bonus_product_name
                                category_id=bonus_product_category_id
                                item_qty_value=0
                                bonus_qty=bonus_item_qty*bfullCount
                                newPrice=0
                                item_vat=0
                                
                                item_unit=bonus_product_unit_type
                                item_carton=bonus_product_item_carton
                                
                                short_note='Bonus Item, Circular '+str(bcircularNo)
                                promotion_type=''
                                bonus_applied_on_qty=0
                                circular_no=str(bcircularNo)
                                
                                #------------ set batch id after checking stock
                                requestBaseQty=bonus_qty
                                
                                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                                for stockRow in stockRows:
                                    batch_id=stockRow.batch_id
                                    quantity=stockRow.quantity
                                    block_qty=stockRow.block_qty
                                    availableQty=quantity-block_qty
                                    
                                    if requestBaseQty<=availableQty:
                                        newBlockQty=block_qty+requestBaseQty
                                        newBaseQty=requestBaseQty
                                        requestBaseQty=0
                                        
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':newBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)                        
                                        stockRow.update_record(block_qty=newBlockQty)                        
                                        break
                                    else:
                                        newBlockQty=block_qty+availableQty
                                        newBaseQty=availableQty
                                        requestBaseQty=requestBaseQty-availableQty
                                        
                                        #--------------
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':newBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)
                                        stockRow.update_record(block_qty=newBlockQty)
                                
                                #--------------
                                #if until_stock_last=='NA':# Until last stock available
                                if requestBaseQty>0:
                                    batch_id=''
                                    emptyBatchFlag=1
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':requestBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    
                                #---------------------------------------                                    
                                promoFlag=1
            
            #-------- step-3: Special rate            
            ordRecords3=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)&(db.sm_tp_rules_temp_process.prio_flag==0)&(db.sm_tp_rules_temp_process.ar_flag==0)&(db.sm_tp_rules_temp_process.pb_flag==0)).select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
            for ordRec in ordRecords3:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                actual_tp=price
                actual_vat=item_vat
                
                for spRateRow in specialRateRows:
                    product_id=str(spRateRow.product_id).strip().upper()
                    min_qty=spRateRow.min_qty
                    special_rate_tp=spRateRow.special_rate_tp
                    special_rate_vat=spRateRow.special_rate_vat
                    
                    allowed_credit_inv=str(spRateRow.allowed_credit_inv).strip().upper()
                    regular_discount_apply=str(spRateRow.regular_discount_apply).strip().upper()
                    
                    if product_id==item_id:
                        allowSpecialRate='YES'
                        if payment_mode!='CASH':
                            if allowed_credit_inv=='NO':
                                allowSpecialRate='NO'                        
                        
                        #check special rate applicable
                        promotion_type=''
                        bonus_applied_on_qty=0
                        circular_no=''
                        
                        if allowSpecialRate=='NO':
                            newPrice=special_rate_tp
                            regular_discount_apply='YES'
                            short_note='Special Rate (Premium TP) and vat applied'
                            actual_tp=special_rate_tp
                            actual_vat=special_rate_vat                            
                        else:
                            if item_qty_value<min_qty:
                                newPrice=special_rate_tp
                                regular_discount_apply='YES'
                                short_note='Special Rate (Premium TP) and vat applied'
                                actual_tp=special_rate_tp
                                actual_vat=special_rate_vat
                            else:
                                newPrice=price
                                regular_discount_apply='NO'
                                short_note='Special Rate and vat applied'
                        
                        newVat=special_rate_vat                                            
                        
                        #-----------
                        bonus_qty=0                        
                        totalAmountTP+=round(item_qty_value*newPrice,6)
                        totalAmountVat+=round(item_qty_value*newVat,6)
                        
                        if regular_discount_apply=='YES': #apply for all qty
                            #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                            declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                            if not declaredItemRow:                                                                       
                                totalAmt+=round(item_qty_value*newPrice,2)                                    
                                short_note+=' and regular discount'
                        
                        #------------ set batch id after checking stock
                        requestBaseQty=item_qty_value
                        
                        stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                        for stockRow in stockRows:
                            batch_id=stockRow.batch_id
                            quantity=stockRow.quantity
                            block_qty=stockRow.block_qty
                            availableQty=quantity-block_qty
                            
                            if requestBaseQty<=availableQty:
                                newBlockQty=block_qty+requestBaseQty
                                newBaseQty=requestBaseQty
                                requestBaseQty=0
                                
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)                        
                                stockRow.update_record(block_qty=newBlockQty)                        
                                break
                            else:
                                newBlockQty=block_qty+availableQty
                                newBaseQty=availableQty
                                requestBaseQty=requestBaseQty-availableQty
                                
                                #--------------
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                stockRow.update_record(block_qty=newBlockQty)
                                
                        #--------------
                        if requestBaseQty>0:
                            batch_id=''
                            emptyBatchFlag=1
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)
                            
                        #---------------------------------------
                        promoFlag=1                        
                        ordRec.update_record(sr_flag=1)
                        break
                        
            #-------- step-4: Flat rate            
            ordRecords4=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)&(db.sm_tp_rules_temp_process.prio_flag==0)&(db.sm_tp_rules_temp_process.ar_flag==0)&(db.sm_tp_rules_temp_process.pb_flag==0)&(db.sm_tp_rules_temp_process.sr_flag==0)).select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
            for ordRec in ordRecords4:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                actual_tp=price
                actual_vat=item_vat
                
                for flatRateRow in flatRateRows:
                    campaign_ref=str(flatRateRow.campaign_ref).strip()
                    product_id=str(flatRateRow.product_id).strip().upper()
                    min_qty=flatRateRow.min_qty
                    flat_rate=flatRateRow.flat_rate #Flat Tp
                    
                    allowed_credit_inv=str(flatRateRow.allowed_credit_inv).strip().upper()
                    regular_discount_apply=str(flatRateRow.regular_discount_apply).strip().upper()
                    allow_bundle=str(flatRateRow.allow_bundle).strip().upper()  #for different processing rules
                    
                    if product_id==item_id and item_qty_value>=min_qty:                        
                        allowFlatRate='YES'
                        if payment_mode!='CASH':
                            if allowed_credit_inv=='NO':
                                allowFlatRate='NO'
                                
                        #check flat rate applicable
                        if allowFlatRate=='NO':
                            break
                            
                        #------------- Allow per bundle calculated and extra will be regular rate
                        
                        if allow_bundle=='YES':
                            regularQty=(item_qty_value%min_qty)
                            fullQty=item_qty_value-regularQty
                            
                            newPrice=flat_rate
                            short_note='Flat Rate applied'
                            promotion_type='FLAT'
                            bonus_applied_on_qty=0
                            circular_no=campaign_ref
                            
                            #-----------
                            
                            bonus_qty=0                            
                            totalAmountTP+=round(fullQty*newPrice,6)
                            totalAmountVat+=round(fullQty*item_vat,6)
                            
                            if regular_discount_apply=='YES': #apply for all qty
                                #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:                                                                       
                                    totalAmt+=round(fullQty*newPrice,2)                                    
                                    short_note+=' and regular discount'
                            
                            #------------ set batch id after checking stock
                            requestBaseQty=fullQty
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                             
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1 
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                            
                              
                            #---------------------------------------                        
                            if regularQty>0:                                                                        
                                short_note='Flat Rate balance regular rate, declared item'
                                promotion_type=''
                                bonus_applied_on_qty=0
                                circular_no=''
                                
                                #-----------
                                bonus_qty=0                            
                                totalAmountTP+=round(regularQty*price,6)
                                totalAmountVat+=round(regularQty*item_vat,6)
                                
                                #-----------
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:
                                    totalAmt+=round(regularQty*price,2)
                                    short_note='Flat Rate balance regular rate and applied regular discount'
                                
                                #------------ set batch id after checking stock
                                requestBaseQty=regularQty
                                
                                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                                for stockRow in stockRows:
                                    batch_id=stockRow.batch_id
                                    quantity=stockRow.quantity
                                    block_qty=stockRow.block_qty
                                    availableQty=quantity-block_qty
                                    
                                    if requestBaseQty<=availableQty:
                                        newBlockQty=block_qty+requestBaseQty
                                        newBaseQty=requestBaseQty
                                        requestBaseQty=0
                                        
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)                        
                                        stockRow.update_record(block_qty=newBlockQty)                        
                                        break
                                    else:
                                        newBlockQty=block_qty+availableQty
                                        newBaseQty=availableQty
                                        requestBaseQty=requestBaseQty-availableQty
                                        
                                        #--------------
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)
                                        stockRow.update_record(block_qty=newBlockQty)
                                        
                                #--------------
                                if requestBaseQty>0:
                                    batch_id=''
                                    emptyBatchFlag=1
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    
                        #---------------------------------------    All quantity regular rate if minimum rate matching                        
                        else:                            
                            fullQty=item_qty_value
                            
                            newPrice=flat_rate                                               
                            short_note='Flat Rate applied'
                            promotion_type='FLAT'
                            bonus_applied_on_qty=0
                            circular_no=campaign_ref
                            
                            #-----------
                            bonus_qty=0
                            
                            totalAmountTP+=round(fullQty*newPrice,6)
                            totalAmountVat+=round(fullQty*item_vat,6)
                            
                            if regular_discount_apply=='YES': #apply for all qty
                                #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:
                                    discountRate=newPrice
                                    #regular rate, applied discount                                    
                                    totalAmt+=round(fullQty*discountRate,2)
                                    short_note+=' and regular discount'
                                    
                            #------------ set batch id after checking stock
                            requestBaseQty=fullQty
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1 
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------
                            
                        promoFlag=1                        
                        ordRec.update_record(fr_flag=1)
                        break
                        
            #-------- promo ref=1 then aproved rate later
            if promo_ref==1:
                #-------- step-1: Approved rate            
                ordRecords1=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)&(db.sm_tp_rules_temp_process.prio_flag==0)&(db.sm_tp_rules_temp_process.pb_flag==0)&(db.sm_tp_rules_temp_process.sr_flag==0)&(db.sm_tp_rules_temp_process.fr_flag==0)).select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
                for ordRec in ordRecords1:             
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)   
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton
                    actual_tp=price
                    actual_vat=item_vat
                
                    for appItemRow in approvedItemRows:
                        product_id=str(appItemRow.product_id).strip().upper()
                        bonus_type=appItemRow.bonus_type
                        fixed_percent_rate=appItemRow.fixed_percent_rate
                        
                        if product_id==item_id:
                            short_note=''
                            newPrice=0
                            promotion_type='APPROVED'
                            bonus_applied_on_qty=0
                            circular_no=''
                            
                            if bonus_type=='Fixed':
                                newPrice=fixed_percent_rate
                                short_note='Approved Fixed Rate '+str(newPrice)+',TP '+str(price)
                            elif bonus_type=='Percentage':
                                newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
                                short_note='Approved '+str(fixed_percent_rate)+'% of TP '+str(price)
                                
                            #-----------
                            bonus_qty=0                        
                            totalAmountTP+=round(item_qty_value*newPrice,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)                
                                                    
                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------
                            
                            promoFlag=1                        
                            ordRec.update_record(ar_flag=1)
                            break
            
            #-------- step-5: Declared Item           
            ordRecords5=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)&(db.sm_tp_rules_temp_process.prio_flag==0)&(db.sm_tp_rules_temp_process.ar_flag==0)&(db.sm_tp_rules_temp_process.pb_flag==0)&(db.sm_tp_rules_temp_process.sr_flag==0)&(db.sm_tp_rules_temp_process.fr_flag==0)&(db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.status=='ACTIVE')&(db.sm_tp_rules_temp_process.item_id==db.sm_promo_declared_item.product_id)).select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
            for ordRec in ordRecords5:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                actual_tp=price
                actual_vat=item_vat
                
                short_note='Declared Item'
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #-----------
                bonus_qty=0
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)
                
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1 
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
                    
                #---------------------------------------                
                promoFlag=1                        
                ordRec.update_record(di_flag=1)
            
            #-------- step-6: Regular Discount            
            ordRec6Qset=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)&(db.sm_tp_rules_temp_process.prio_flag==0)&(db.sm_tp_rules_temp_process.ar_flag==0)&(db.sm_tp_rules_temp_process.pb_flag==0)&(db.sm_tp_rules_temp_process.sr_flag==0)&(db.sm_tp_rules_temp_process.fr_flag==0)&(db.sm_tp_rules_temp_process.di_flag==0))
            ordRec6Rows=ordRec6Qset.select(db.sm_tp_rules_temp_process.quantity,db.sm_tp_rules_temp_process.price,db.sm_tp_rules_temp_process.item_vat)
            if ordRec6Rows:                
            #     for ordRec6Row in ordRec6Rows:
            #         quantity=ordRec6Row.quantity
            #         price=ordRec6Row.price
            #         #item_vat=ordRec6Row.item_vat
            #         totalAmt+=quantity*price
            #
            # # discount calculation
            # discountRows=db((db.sm_promo_regular_discount.cid==c_id)&(db.sm_promo_regular_discount.from_date<=orderDate)&(db.sm_promo_regular_discount.to_date>=orderDate) & (db.sm_promo_regular_discount.status=='ACTIVE')&(db.sm_promo_regular_discount.min_amount<=totalAmt)).select(db.sm_promo_regular_discount.discount_precent,orderby=~db.sm_promo_regular_discount.min_amount,limitby=(0,1))
            # if discountRows:
            #     discount_precent=discountRows[0].discount_precent
            #
            #     discount=round((totalAmt*discount_precent)/100,2)
                
                ordRecords6=ordRec6Qset.select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
                for ordRec in ordRecords6:             
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton
                    actual_tp=price
                    actual_vat=item_vat
                
                    short_note='Regular Discount'
                    promotion_type=''
                    bonus_applied_on_qty=0
                    circular_no=''
                    
                    #-----------
                    bonus_qty=0
                    totalAmountTP+=round(item_qty_value*price,6)
                    totalAmountVat+=round(item_qty_value*item_vat,6)
                    
                    #------------ set batch id after checking stock
                    requestBaseQty=item_qty_value
                    
                    stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                    for stockRow in stockRows:
                        batch_id=stockRow.batch_id
                        quantity=stockRow.quantity
                        block_qty=stockRow.block_qty
                        availableQty=quantity-block_qty
                        
                        if requestBaseQty<=availableQty:
                            newBlockQty=block_qty+requestBaseQty
                            newBaseQty=requestBaseQty
                            requestBaseQty=0
                            
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)                        
                            stockRow.update_record(block_qty=newBlockQty)                        
                            break
                        else:
                            newBlockQty=block_qty+availableQty
                            newBaseQty=availableQty
                            requestBaseQty=requestBaseQty-availableQty
                            
                            #--------------
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)
                            stockRow.update_record(block_qty=newBlockQty)
                            
                    #--------------
                    if requestBaseQty>0:
                        
                        batch_id=''
                        emptyBatchFlag=1        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        
                    #---------------------------------------                    
                    promoFlag=1
                    ordRec.update_record(rd_flag=1)

            ###7 discount for all
            ordRec7Qset = db((db.sm_tp_rules_temp_process.cid == c_id) & (db.sm_tp_rules_temp_process.depot_id == depot_id) & (
                            db.sm_tp_rules_temp_process.sl == order_sl))
            ordRec7Rows = ordRec7Qset.select(db.sm_tp_rules_temp_process.quantity, db.sm_tp_rules_temp_process.price,
                                             db.sm_tp_rules_temp_process.item_vat)
            if ordRec7Rows:
                totalAmt=0
                for ordRec7Row in ordRec7Rows:
                        quantity=ordRec7Row.quantity
                        price=ordRec7Row.price
                        #item_vat=ordRec6Row.item_vat
                        totalAmt+=quantity*price

                # discount calculation
                discountRows=db((db.sm_promo_regular_discount.cid==c_id)&(db.sm_promo_regular_discount.from_date<=orderDate)&(db.sm_promo_regular_discount.to_date>=orderDate) & (db.sm_promo_regular_discount.status=='ACTIVE')&(db.sm_promo_regular_discount.min_amount<=totalAmt)).select(db.sm_promo_regular_discount.discount_precent,orderby=~db.sm_promo_regular_discount.min_amount,limitby=(0,1))
                if discountRows:
                    discount_precent=discountRows[0].discount_precent

                    discount=round((totalAmt*discount_precent)/100,2)

            #------------ step-Last
            ordRecordsLast=db((db.sm_tp_rules_temp_process.cid==c_id) & (db.sm_tp_rules_temp_process.depot_id==depot_id)&(db.sm_tp_rules_temp_process.sl==order_sl)&(db.sm_tp_rules_temp_process.prio_flag==0)&(db.sm_tp_rules_temp_process.ar_flag==0)&(db.sm_tp_rules_temp_process.pb_flag==0)&(db.sm_tp_rules_temp_process.sr_flag==0)&(db.sm_tp_rules_temp_process.fr_flag==0)&(db.sm_tp_rules_temp_process.di_flag==0)&(db.sm_tp_rules_temp_process.rd_flag==0)).select(db.sm_tp_rules_temp_process.ALL,orderby=db.sm_tp_rules_temp_process.item_name)
            for ordRec in ordRecordsLast:
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)   
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                actual_tp=price
                actual_vat=item_vat
                
                bonus_qty=0                
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)            
                short_note='-'
                
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'category_id':category_id,'quantity':item_qty_value,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'note':req_note,'short_note':short_note,'status':'Submitted'}
                #detailList.append(detailDict)
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)                        
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        stockRow.update_record(block_qty=newBlockQty)
                        
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
                    
                #---------------------------------------
                
    discount=round(float(discount),2)
    totalAmount=(round(totalAmountTP,2)+round(totalAmountVat,2)-discount)
    sp_discount=round(float(sp_discount),2)
    
    retMsg=''
    #=============== Insert invoice head and details
    if (len(headList)> 0 and len(detailList) > 0):
        
        #----------- check credit policy
        limitOverFlag=0
        acknowledge_flag=0
        if payment_mode!='CASH':
            acknowledge_flag=1
            
            creditPolicyRow=db((db.sm_cp_approved.cid==c_id)&(db.sm_cp_approved.client_id==client_id)&(db.sm_cp_approved.status=='ACTIVE')).select(db.sm_cp_approved.credit_amount,limitby=(0,1))
            if not creditPolicyRow:
                limitOverFlag=1
            else:
                credit_amount=creditPolicyRow[0].credit_amount
                
                tx_closing_balance=0
                ledgerRow=db((db.sm_transaction.cid==c_id)&(db.sm_transaction.tx_account=='CLT-'+str(client_id))&(db.sm_transaction.opposite_account=='DPT-'+str(depot_id))).select(db.sm_transaction.tx_closing_balance,orderby=~db.sm_transaction.tx_date,limitby=(0,1))
                if ledgerRow:
                    tx_closing_balance=ledgerRow[0].tx_closing_balance            
                clientTotal=tx_closing_balance+totalAmount
                
                if clientTotal>credit_amount:
                    limitOverFlag=1
                    
        #----------- end check credit policy        
        level0_id=''
        level0_name=''
        level1_id=''
        level1_name=''
        level2_id=''
        level2_name=''
        level3_id=''
        level3_name=''
        orderHRow=db((db.sm_order_head.cid==c_id) & (db.sm_order_head.depot_id==depot_id) &(db.sm_order_head.sl==sl)).select(db.sm_order_head.level0_id,db.sm_order_head.level0_name,db.sm_order_head.level1_id,db.sm_order_head.level1_name,db.sm_order_head.level2_id,db.sm_order_head.level2_name,db.sm_order_head.level3_id,db.sm_order_head.level3_name,limitby=(0,1))
        if orderHRow:
            level0_id=orderHRow[0].level0_id
            level0_name=orderHRow[0].level0_name
            level1_id=orderHRow[0].level1_id
            level1_name=orderHRow[0].level1_name
            level2_id=orderHRow[0].level2_id
            level2_name=orderHRow[0].level2_name
            level3_id=orderHRow[0].level3_id
            level3_name=orderHRow[0].level3_name
            
        #---------- dicount amount assigned
        for i in range(len(headList)):
            headDictData=headList[i]
            headDictData['discount']=discount
            headDictData['client_limit_over']=limitOverFlag
            headDictData['empty_batch_flag']=emptyBatchFlag
            headDictData['acknowledge_flag']=acknowledge_flag
            headDictData['level0_id']=level0_id
            headDictData['level0_name']=level0_name
            headDictData['level1_id']=level1_id
            headDictData['level1_name']=level1_name
            headDictData['level2_id']=level2_id
            headDictData['level2_name']=level2_name
            headDictData['level3_id']=level3_id
            headDictData['level3_name']=level3_name
            headDictData['discount_precent']=discount_precent
            headDictData['sp_discount']=sp_discount
            
        for j in range(len(detailList)):
            detailDictData=detailList[j]
            detailDictData['discount']=discount
            detailDictData['level0_id']=level0_id
            detailDictData['level0_name']=level0_name
            detailDictData['level1_id']=level1_id
            detailDictData['level1_name']=level1_name
            detailDictData['level2_id']=level2_id
            detailDictData['level2_name']=level2_name
            detailDictData['level3_id']=level3_id
            detailDictData['level3_name']=level3_name
            
        #-------------
        #Update status of head and detail                
        rows=db.sm_invoice.bulk_insert(detailList)
        rows=db.sm_invoice_head.bulk_insert(headList)                        
        db((db.sm_order_head.cid==c_id) & (db.sm_order_head.depot_id==depot_id) &(db.sm_order_head.sl==sl)).update(status='Invoiced',invoice_ref=maxSl,flag_data='1',field2=1)#delivery_date=req_delivery_date,
        
        retMsg='Successfully Imported'
        db.commit()        
    #-------------- end order
    
    return retMsg+','+str(maxSl)
    
#***** new invoice with promotion and credit limit
# change:- parameter, insert into temp, sm_tp_rules_temp_process->sm_tp_rules_temp_process_manual, order_sl->invoice_sl

def get_order_to_delivery_detail_rules_manual(cid,depot_id,invoice_sl,order_sl,clientId,orderDate):
    c_id=cid
    depot_id=depot_id
    sl=order_sl
    client_id=clientId
    orderDate=orderDate #Q? it is current date or order date, now orderDate used?
    
    #------------  insert into temp
    # Head Loop
    
    promo_ref=0
    
    invoiceHeadRecords=db((db.sm_invoice_head.cid==c_id)&(db.sm_invoice_head.depot_id==depot_id)&(db.sm_invoice_head.sl==invoice_sl)&(db.sm_invoice_head.status=='Draft')).select(db.sm_invoice_head.ALL,limitby=(0,1))
    if not invoiceHeadRecords:
        return 'Invalid request'
    else:
        depot_id=invoiceHeadRecords[0].depot_id
        depot_name=invoiceHeadRecords[0].depot_name
        store_id=invoiceHeadRecords[0].store_id
        store_name=invoiceHeadRecords[0].store_name
        
        client_name=invoiceHeadRecords[0].client_name
        rep_id=invoiceHeadRecords[0].rep_id
        rep_name=invoiceHeadRecords[0].rep_name
        order_date=invoiceHeadRecords[0].order_datetime#order_date
        order_datetime=invoiceHeadRecords[0].order_datetime
        delivery_date=invoiceHeadRecords[0].delivery_date
        payment_mode=invoiceHeadRecords[0].payment_mode
        area_id=invoiceHeadRecords[0].area_id
        area_name=invoiceHeadRecords[0].area_name
        order_media=invoiceHeadRecords[0].invoice_media
        ym_date=invoiceHeadRecords[0].ym_date
        client_cat=''#invoiceHeadRecords[0].client_cat
        note=invoiceHeadRecords[0].note
        market_id=invoiceHeadRecords[0].market_id
        market_name=invoiceHeadRecords[0].market_name
        
        promo_ref=invoiceHeadRecords[0].promo_ref  
        if promo_ref!=0:
            promo_ref=1
                
        orderRows=db((db.sm_invoice.cid==c_id) & (db.sm_invoice.depot_id==depot_id)&(db.sm_invoice.sl==invoice_sl)).select(db.sm_invoice.ALL,orderby=db.sm_invoice.item_id)
        detailList=[]
        for ordRow in orderRows:
            item_id=str(ordRow.item_id).strip().upper()
            item_name=ordRow.item_name
            category_id=ordRow.category_id
            actual_tp=ordRow.actual_tp
            actual_vat=ordRow.actual_vat
            quantity=ordRow.quantity
            price=ordRow.price
            item_vat=ordRow.item_vat
            item_unit=ordRow.item_unit
            item_carton=ordRow.item_carton
            sp_discount_item=ordRow.sp_discount_item
            
            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':invoice_sl,'store_id':store_id,'store_name':store_name,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'order_date':order_date,'order_datetime':order_datetime,'delivery_date':delivery_date,
                        'payment_mode':payment_mode,'area_id':area_id,'area_name':area_name,'order_media':order_media,'ym_date':ym_date,'client_cat':client_cat,'note':note,'item_id':item_id,'item_name':item_name,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':quantity,'price':price,'item_vat':item_vat,'item_unit':item_unit,'item_carton':item_carton}
            detailList.append(detailDict)
            
        #delete temp
        db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)).delete()
        
        #insert temp
        db.sm_tp_rules_temp_process_manual.bulk_insert(detailList)
        
    #========================-get settings flag
    invoiceRulesFlag=False
    
    compSttRows=db((db.sm_settings.cid==c_id)&(db.sm_settings.s_key=='INVOICE_RULES')&(db.sm_settings.s_value=='YES')).select(db.sm_settings.cid,limitby=(0,1))
    if compSttRows:
        invoiceRulesFlag=True
        
    #================ if invoice rules are to apply (Note: ANY or Sepcific item, at a time two rules not applicable)
    productBonusPriorityRows=''
    approvedItemRows=''    
    productBonusRows=''
    specialRateRows=''
    flatRateRows=''
    
    if invoiceRulesFlag==True:
        approvedItemRows=db((db.sm_promo_approved_rate.cid==c_id)&(db.sm_promo_approved_rate.client_id==client_id)&(db.sm_promo_approved_rate.from_date<=orderDate)&(db.sm_promo_approved_rate.to_date>=orderDate)&(db.sm_promo_approved_rate.status=='ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date|db.sm_promo_approved_rate.product_id)
        productBonusRows=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,db.sm_promo_product_bonus.until_stock_last,db.sm_promo_product_bonus.allowed_credit_inv,db.sm_promo_product_bonus.regular_discount_apply,orderby=~db.sm_promo_product_bonus.min_qty)       #&(db.sm_promo_product_bonus.id!=promo_ref)
        specialRateRows=db((db.sm_promo_special_rate.cid==c_id)&(db.sm_promo_special_rate.from_date<=orderDate)&(db.sm_promo_special_rate.to_date>=orderDate)&(db.sm_promo_special_rate.status=='ACTIVE')).select(db.sm_promo_special_rate.product_id,db.sm_promo_special_rate.min_qty,db.sm_promo_special_rate.special_rate_tp,db.sm_promo_special_rate.special_rate_vat,db.sm_promo_special_rate.allowed_credit_inv,db.sm_promo_special_rate.regular_discount_apply,orderby=~db.sm_promo_special_rate.from_date)
        flatRateRows=db((db.sm_promo_flat_rate.cid==c_id)&(db.sm_promo_flat_rate.from_date<=orderDate)&(db.sm_promo_flat_rate.to_date>=orderDate)&(db.sm_promo_flat_rate.status=='ACTIVE')).select(db.sm_promo_flat_rate.campaign_ref,db.sm_promo_flat_rate.product_id,db.sm_promo_flat_rate.min_qty,db.sm_promo_flat_rate.flat_rate,db.sm_promo_flat_rate.allowed_credit_inv,db.sm_promo_flat_rate.regular_discount_apply,db.sm_promo_flat_rate.allow_bundle,orderby=~db.sm_promo_flat_rate.from_date)

        # common approved rate
        #approvedItemRows = db((db.sm_promo_approved_rate.cid == c_id) & (db.sm_promo_approved_rate.from_date <= orderDate) & (db.sm_promo_approved_rate.to_date >= orderDate) & (db.sm_promo_approved_rate.status == 'ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date | db.sm_promo_approved_rate.product_id)

    #----------- 
    maxSl=invoice_sl
    
    records=''
    #---------------   order detail records
    depot_name=''    
    client_name=''
    rep_id=''
    rep_name=''
    area_id=''
    area_name=''
    order_datetime=''
    payment_mode=''
    req_note=''
    ym_date=''
    req_delivery_date=''
    
    #----------------
    headList=[]                                               
    detailDict={}
    detailList=[]                            
    headFlag=False
    
    totalAmountTP=0
    totalAmountVat=0
    discount=0
    sp_discount=0 
    discount_precent=0
    #order details loop      
    orderRecords=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)).select(db.sm_tp_rules_temp_process_manual.ALL,limitby=(0,1))
    if orderRecords:
        depot_name=orderRecords[0].depot_name
        store_id=orderRecords[0].store_id
        store_name=orderRecords[0].store_name
        client_id=orderRecords[0].client_id
        client_name=orderRecords[0].client_name
        clientCategory=orderRecords[0].client_cat
        rep_id=orderRecords[0].rep_id
        rep_name=orderRecords[0].rep_name
        area_id=orderRecords[0].area_id
        area_name=orderRecords[0].area_name                                
        order_datetime=orderRecords[0].order_datetime
        order_media=orderRecords[0].order_media
        delivery_date=orderRecords[0].delivery_date
        payment_mode=orderRecords[0].payment_mode
        req_note=orderRecords[0].note
        market_id=orderRecords[0].market_id
        market_name=orderRecords[0].market_name
        
        #---delivery date get from order date
        ym_date=str(delivery_date)[0:7]+'-01'
        req_delivery_date=str(delivery_date)[0:10]
        
        #head records
        headDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'store_id':store_id,'store_name':store_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,'invoice_media':order_media,'area_id':area_id,'area_name':area_name,'status':'Submitted','ym_date':ym_date,'promo_ref':promo_ref}
        headList.append(headDict)
        
        emptyBatchFlag=0
        if invoiceRulesFlag==False:
            #=========================== Rules not apply
            ordRecords=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRecord in ordRecords:
                item_id=str(ordRecord.item_id).strip().upper()
                item_name=ordRecord.item_name
                category_id=ordRecord.category_id
                actual_tp=ordRecord.actual_tp
                actual_vat=ordRecord.actual_vat
                item_qty_value=int(ordRecord.quantity)
                price=float(ordRecord.price)   
                item_vat=float(ordRecord.item_vat)
                item_unit=ordRecord.item_unit
                item_carton=ordRecord.item_carton
                
                #-----------
                bonus_qty=0
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)
                short_note=''                
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)                        
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        stockRow.update_record(block_qty=newBlockQty)
                        
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
                    
        else:
            #===================== Rules apply 
            promoFlag=0
            totalAmt=0
            
            #-------- step-0: Priority (Product Bonus) 
            
            if promo_ref==0:
                #-------- step-1: Approved rate            
                ordRecords1=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
                for ordRec in ordRecords1:             
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    actual_tp=ordRec.actual_tp
                    actual_vat=ordRec.actual_vat
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)   
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton
                
                    for appItemRow in approvedItemRows:
                        product_id=str(appItemRow.product_id).strip().upper()
                        bonus_type=appItemRow.bonus_type
                        fixed_percent_rate=appItemRow.fixed_percent_rate
                        
                        if product_id==item_id:
                            short_note=''
                            newPrice=0
                            
                            promotion_type='APPROVED'
                            bonus_applied_on_qty=0
                            circular_no=''
                            
                            if bonus_type=='Fixed':
                                newPrice=fixed_percent_rate
                                short_note='Approved Fixed Rate '+str(newPrice)+',TP '+str(price)
                            elif bonus_type=='Percentage':
                                newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
                                short_note='Approved '+str(fixed_percent_rate)+'% of TP '+str(price)
                            #-----------
                            bonus_qty=0                        
                            totalAmountTP+=round(item_qty_value*newPrice,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)                
                                                    
                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                            
                            promoFlag=1                        
                            ordRec.update_record(ar_flag=1)
                            break
            
            #-------- step-2: Product Bonus
            for prodBonusRow in productBonusRows:      
                rowid=prodBonusRow.id
                circular_number=prodBonusRow.circular_number
                min_qty=prodBonusRow.min_qty
                #until_stock_last=str(prodBonusRow.until_stock_last).strip().upper()          #for bonus
                allowed_credit_inv=str(prodBonusRow.allowed_credit_inv).strip().upper()      #for bonus
                regular_discount_apply=str(prodBonusRow.regular_discount_apply).strip().upper()  #for product full qty
                
                allowBonus='YES'
                if payment_mode!='CASH':
                    if allowed_credit_inv=='NO':
                        allowBonus='NO'
                
                if allowBonus=='NO':
                    continue
                    
                pbQset=db((db.sm_promo_product_bonus_products.cid==c_id)&(db.sm_promo_product_bonus_products.refrowid==rowid)&(db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_promo_product_bonus_products.product_id==db.sm_tp_rules_temp_process_manual.item_id))
                totalQtyRows=pbQset.select(db.sm_tp_rules_temp_process_manual.quantity.sum(),groupby=db.sm_tp_rules_temp_process_manual.cid)
                
                if totalQtyRows:
                    qtyCount=totalQtyRows[0][db.sm_tp_rules_temp_process_manual.quantity.sum()]
                    
                    if qtyCount>=min_qty:                        
                        fullCount=int(qtyCount/min_qty)
                        
                        #===================================== for bonus calculate
                        circularStr=circular_number
                        
                        nextQtyCount=qtyCount-min_qty*fullCount
                        
                        regularQty=0       #extra Qty
                        discountRate=0
                        
                        itemFullQty=min_qty*fullCount
                        
                        bonusDictList=[]
                        bonusDictList.append({'rowid':rowid,'fullCount':fullCount,'circularNo':circular_number})
                        
                        if nextQtyCount>0:
                            prodPromList=[]
                            totalItemRows=pbQset.select(db.sm_tp_rules_temp_process_manual.item_id,groupby=db.sm_tp_rules_temp_process_manual.item_id)
                            for totItemRow in totalItemRows:                            
                                prodPromList.append(totItemRow.item_id)
                                
                            productBonusRows2=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')&(db.sm_promo_product_bonus.id!=rowid)&(db.sm_promo_product_bonus.id==db.sm_promo_product_bonus_products.refrowid)&(db.sm_promo_product_bonus_products.product_id.belongs(prodPromList))).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,orderby=~db.sm_promo_product_bonus.min_qty,groupby=db.sm_promo_product_bonus.id)
                            if productBonusRows2:                            
                                for productBonusRow2 in productBonusRows2:      
                                    rowid2=productBonusRow2.id
                                    circular_number2=productBonusRow2.circular_number
                                    min_qty2=productBonusRow2.min_qty
                                    
                                    if nextQtyCount>=min_qty2:
                                        fullCount2=int(nextQtyCount/min_qty2)
                                        
                                        circularStr+=','+str(circular_number2)
                                        bonusDictList.append({'rowid':rowid2,'fullCount':fullCount2,'circularNo':circular_number2})
                                        
                                        nextQtyCount=nextQtyCount-min_qty2*fullCount2
                                        itemFullQty+=min_qty2*fullCount2
                                              
                                    else:                                        
                                        break
                                        
                                if nextQtyCount>0:
                                    regularQty=nextQtyCount
                                    #discount apply
                            else:
                                regularQty=nextQtyCount
                                #discount apply
                        
                        #---------------- bonus stock available check                
#                         bonusStockFlag='YES'
#                         bonusItemList=[]                        
#                         #--------- bonus item qty available check                        
#                         for k in range(len(bonusDictList)):
#                             bonusDictData=bonusDictList[k]                            
#                             bRowid=bonusDictData['rowid']
#                             bfullCount=bonusDictData['fullCount']
#                             
#                             bonusRows=db((db.sm_promo_product_bonus_bonuses.cid==c_id)&(db.sm_promo_product_bonus_bonuses.refrowid==bRowid)).select(db.sm_promo_product_bonus_bonuses.bonus_product_id,db.sm_promo_product_bonus_bonuses.bonus_qty)
#                             for bonusRow in bonusRows:
#                                 item_id=bonusRow.bonus_product_id                                
#                                 bonus_qty=bonusRow.bonus_qty*bfullCount                                
#                                 get_index=-1
#                                 try:
#                                     get_index=map(itemgetter('item_id'), bonusItemList).index(item_id)    
#                                 except:
#                                     get_index=-1                   
#                                     
#                                 if get_index==-1:
#                                     bonusItemList.append({'item_id':item_id,'item_qty':bonus_qty})                                
#                                 else:      
#                                     for z in range(len(bonusItemList)):
#                                         bonusItemData=bonusItemList[z]
#                                         bonusItemId=bonusItemData['item_id']
#                                         bonusItemQty=bonusItemData['item_qty']                                        
#                                         if bonusItemId==item_id:
#                                             bonusItemData['item_qty']=int(bonus_qty+bonusItemQty)
#                                             break
#                         
#                         #--------- bonus item qty available check                        
#                         for m in range(len(bonusItemList)):
#                             b_bonusDictData=bonusItemList[m]                            
#                             b_item_id=b_bonusDictData['item_id']
#                             b_item_qty=b_bonusDictData['item_qty']
#                             
#                             stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==b_item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.quantity.sum(),db.sm_depot_stock_balance.block_qty.sum(),groupby=db.sm_depot_stock_balance.item_id)
#                             if stockRows:
#                                 for stockRow in stockRows:                                
#                                     quantity=stockRow[db.sm_depot_stock_balance.quantity.sum()]
#                                     block_qty=stockRow[db.sm_depot_stock_balance.block_qty.sum()]
#                                     availableQty=quantity-block_qty                                
#                                     if b_item_qty>availableQty:
#                                         bonusStockFlag='NO'
#                                         break
#                                 if bonusStockFlag=='NO':
#                                     break                            
#                             else:
#                                 bonusStockFlag='NO'
#                                 break
#                                     
#                         if bonusStockFlag=='NO':
#                             regular_discount_apply='YES'    #regular discount for all items
                        
                        #------ insert and update flag
                        regularQtyDisFlag='YES'
                        bonusOnQty=itemFullQty
                        regularQtyAmt=0

                        ordRecords2=pbQset.select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
                        for ordRec in ordRecords2:
                            item_id=str(ordRec.item_id).strip().upper()
                            item_name=ordRec.item_name
                            category_id=ordRec.category_id
                            actual_tp=ordRec.actual_tp
                            actual_vat=ordRec.actual_vat
                            item_qty_value=int(ordRec.quantity)
                            price=float(ordRec.price)
                            item_vat=float(ordRec.item_vat)
                            item_unit=ordRec.item_unit
                            item_carton=ordRec.item_carton

                            #------------------
                            discount_rate=price

                            specialNote=''
                            for spRateRow in specialRateRows:
                                product_id=str(spRateRow.product_id).strip().upper()
                                minQty=spRateRow.min_qty
                                special_rate_tp=spRateRow.special_rate_tp
                                special_rate_vat=spRateRow.special_rate_vat
                                allowed_credit_inv=str(spRateRow.allowed_credit_inv).strip().upper()
                                if product_id==item_id:
                                    allowSpecialRate='YES'
                                    if payment_mode!='CASH':
                                        if allowed_credit_inv=='NO':
                                            allowSpecialRate='NO'

                                    #check special rate applicable
                                    if allowSpecialRate=='NO':
                                        price=special_rate_tp
                                        item_vat=special_rate_vat
                                        regular_discount_apply='YES'
                                        specialNote=' with Special Rate (Premium TP) and vat applied'
                                        actual_tp=special_rate_tp
                                        actual_vat=special_rate_vat
                                        break
                                    else:
                                        if item_qty_value<minQty:
                                            price=special_rate_tp
                                            item_vat=special_rate_vat
                                            regular_discount_apply='YES'
                                            specialNote=' with Special Rate (Premium TP) and vat applied'
                                            actual_tp=special_rate_tp
                                            actual_vat=special_rate_vat
                                            break
                                        else:
                                            regular_discount_apply='NO'
                                            regularQtyDisFlag='NO'
                                            break
                            #-----------
                            bonus_qty=0
                            totalAmountTP+=round(item_qty_value*price,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)
                            short_note='Bonus apply, Circular '+str(circularStr)+str(specialNote)

                            regQty=0
                            promotion_type='BONUS'
                            if bonusOnQty>item_qty_value:
                                bonus_applied_on_qty=item_qty_value
                                bonusOnQty=bonusOnQty-item_qty_value
                            else:
                                bonus_applied_on_qty=bonusOnQty

                                regQty=int(item_qty_value-bonusOnQty)
                                bonusOnQty=0

                            circular_no=str(circularStr)

                            #----------- new code
                            declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                            if not declaredItemRow:
                                discountRate=discount_rate
                                #regular rate, applied discount

                                if regular_discount_apply=='YES': #apply for all qty
                                    totalAmt+=round(item_qty_value*price,2)
                                    short_note+=' and regular discount'
                                else:
                                    if regularQty>0 and regQty>0:
                                        if regularQtyDisFlag=='YES':
                                            #short_note+=' and regular discount on '+str(regularQty)+' Quantity'
                                            short_note+=' and regular discount on '+str(regQty)+' Quantity'
                                            regularQtyAmt+=regQty*price

                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value

                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty

                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0

                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty

                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)

                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)

                            #---------------------------------------
                            promoFlag=1
                            ordRec.update_record(pb_flag=1)

                        if regular_discount_apply!='YES': #apply for all qty
                            #new code
                            #product bonus rest qty discount apply
                            if regularQtyDisFlag=='YES':
                                #totalAmt+=round(regularQty*discountRate,2)
                                totalAmt+=round(regularQtyAmt,2)

                        #if bonusStockFlag=='YES':
                        #--------- bonus item insert
                        for k in range(len(bonusDictList)):
                            bonusDictData=bonusDictList[k]

                            bRowid=bonusDictData['rowid']
                            bfullCount=bonusDictData['fullCount']
                            bcircularNo=bonusDictData['circularNo']
                            #end new code next use bRowid

                            #--------- bonus item add
                            bonusRows=db((db.sm_promo_product_bonus_bonuses.cid==c_id)&(db.sm_promo_product_bonus_bonuses.refrowid==bRowid)&(db.sm_item.cid==c_id)&(db.sm_item.item_id==db.sm_promo_product_bonus_bonuses.bonus_product_id)).select(db.sm_promo_product_bonus_bonuses.bonus_product_id,db.sm_item.name,db.sm_item.category_id,db.sm_item.category_id_sp,db.sm_item.unit_type,db.sm_item.item_carton,db.sm_promo_product_bonus_bonuses.bonus_qty)
                            for bonusRow in bonusRows:
                                bonus_product_id=bonusRow.sm_promo_product_bonus_bonuses.bonus_product_id
                                bonus_product_name=bonusRow.sm_item.name
                                bonus_product_category_id=bonusRow.sm_item.category_id
                                bonus_product_category_id_sp=bonusRow.sm_item.category_id_sp
                                bonus_item_qty=bonusRow.sm_promo_product_bonus_bonuses.bonus_qty
                                bonus_product_unit_type=bonusRow.sm_item.unit_type
                                bonus_product_item_carton=bonusRow.sm_item.item_carton
                                actual_tp=0
                                actual_vat=0
                                #----
                                item_id=bonus_product_id
                                item_name=bonus_product_name
                                category_id=bonus_product_category_id
                                item_qty_value=0
                                bonus_qty=bonus_item_qty*bfullCount
                                newPrice=0
                                item_vat=0
                                item_unit=bonus_product_unit_type
                                item_carton=bonus_product_item_carton

                                short_note='Bonus Item, Circular '+str(bcircularNo)
                                promotion_type=''
                                bonus_applied_on_qty=0
                                circular_no=str(bcircularNo)

                                #------------ set batch id after checking stock
                                requestBaseQty=bonus_qty

                                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                                for stockRow in stockRows:
                                    batch_id=stockRow.batch_id
                                    quantity=stockRow.quantity
                                    block_qty=stockRow.block_qty
                                    availableQty=quantity-block_qty

                                    if requestBaseQty<=availableQty:
                                        newBlockQty=block_qty+requestBaseQty
                                        newBaseQty=requestBaseQty
                                        requestBaseQty=0

                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':newBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)
                                        stockRow.update_record(block_qty=newBlockQty)
                                        break
                                    else:
                                        newBlockQty=block_qty+availableQty
                                        newBaseQty=availableQty
                                        requestBaseQty=requestBaseQty-availableQty

                                        #--------------
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':newBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)
                                        stockRow.update_record(block_qty=newBlockQty)

                                #--------------
                                #if until_stock_last=='NA':# Until last stock available
                                if requestBaseQty>0:
                                    batch_id=''
                                    emptyBatchFlag=1
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':requestBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                
                                #---------------------------------------                                
                                promoFlag=1
                    
                    #------------
            
            #-------- step-3: Special rate            
            ordRecords3=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRec in ordRecords3:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                
                for spRateRow in specialRateRows:
                    product_id=str(spRateRow.product_id).strip().upper()
                    min_qty=spRateRow.min_qty
                    special_rate_tp=spRateRow.special_rate_tp
                    special_rate_vat=spRateRow.special_rate_vat
                    
                    allowed_credit_inv=str(spRateRow.allowed_credit_inv).strip().upper()
                    regular_discount_apply=str(spRateRow.regular_discount_apply).strip().upper()
                    
                    if product_id==item_id:
                        allowSpecialRate='YES'
                        if payment_mode!='CASH':
                            if allowed_credit_inv=='NO':
                                allowSpecialRate='NO'                        
                        
                        #check special rate applicable       
                        promotion_type=''
                        bonus_applied_on_qty=0
                        circular_no=''                 
                        if allowSpecialRate=='NO':
                            newPrice=special_rate_tp
                            regular_discount_apply='YES'
                            short_note='Special Rate (Premium TP) and vat applied'
                            actual_tp=special_rate_tp
                            actual_vat=special_rate_vat                            
                        else:
                            if item_qty_value<min_qty:
                                newPrice=special_rate_tp
                                regular_discount_apply='YES'
                                short_note='Special Rate (Premium TP) and vat applied'                            
                                actual_tp=special_rate_tp
                                actual_vat=special_rate_vat                            
                            else:
                                newPrice=price
                                regular_discount_apply='NO'
                                short_note='Special Rate and vat applied'
                        
                        newVat=special_rate_vat 
                        
                        #-----------
                        bonus_qty=0                        
                        totalAmountTP+=round(item_qty_value*newPrice,6)
                        totalAmountVat+=round(item_qty_value*newVat,6)
                        
                        if regular_discount_apply=='YES': #apply for all qty
                            #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                            declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                            if not declaredItemRow:                                                                       
                                totalAmt+=round(item_qty_value*newPrice,2)                                    
                                short_note+=' and regular discount'
                                
                        #------------ set batch id after checking stock
                        requestBaseQty=item_qty_value
                        
                        stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                        for stockRow in stockRows:
                            batch_id=stockRow.batch_id
                            quantity=stockRow.quantity
                            block_qty=stockRow.block_qty
                            availableQty=quantity-block_qty
                            
                            if requestBaseQty<=availableQty:
                                newBlockQty=block_qty+requestBaseQty
                                newBaseQty=requestBaseQty
                                requestBaseQty=0
                                
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)                        
                                stockRow.update_record(block_qty=newBlockQty)                        
                                break
                            else:
                                newBlockQty=block_qty+availableQty
                                newBaseQty=availableQty
                                requestBaseQty=requestBaseQty-availableQty
                                
                                #--------------
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                stockRow.update_record(block_qty=newBlockQty)
                        
                        #--------------
                        if requestBaseQty>0:
                            batch_id=''
                            emptyBatchFlag=1
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)
                            
                        #---------------------------------------                        
                        promoFlag=1                        
                        ordRec.update_record(sr_flag=1)
                        break
                        
            #-------- step-4: Flat rate            
            ordRecords4=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRec in ordRecords4:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                            
                for flatRateRow in flatRateRows:
                    campaign_ref=str(flatRateRow.campaign_ref).strip()
                    product_id=str(flatRateRow.product_id).strip().upper()
                    min_qty=flatRateRow.min_qty
                    flat_rate=flatRateRow.flat_rate
                    
                    allowed_credit_inv=str(flatRateRow.allowed_credit_inv).strip().upper()
                    regular_discount_apply=str(flatRateRow.regular_discount_apply).strip().upper()
                    allow_bundle=str(flatRateRow.allow_bundle).strip().upper()  #for different processing rules
                    
                    if product_id==item_id and item_qty_value>=min_qty:
                        allowFlatRate='YES'
                        if payment_mode!='CASH':
                            if allowed_credit_inv=='NO':
                                allowFlatRate='NO'
                        
                        #check flat rate applicable
                        if allowFlatRate=='NO':
                            break
                        
                        #------------------------------Allow per bundle calculated and extra will be regular rate
                        if allow_bundle=='YES':                        
                            regularQty=(item_qty_value%min_qty)
                            fullQty=item_qty_value-regularQty
                            
                            newPrice=flat_rate                                               
                            short_note='Flat Rate applied'
                            promotion_type='FLAT'
                            bonus_applied_on_qty=0
                            circular_no=campaign_ref
                            
                            #-----------
                            bonus_qty=0
                            
                            totalAmountTP+=round(fullQty*newPrice,6)
                            totalAmountVat+=round(fullQty*item_vat,6)
                            
                            if regular_discount_apply=='YES': #apply for all qty
                                #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:                                                                       
                                    totalAmt+=round(fullQty*newPrice,2)                                    
                                    short_note+=' and regular discount'
                            
                            #------------ set batch id after checking stock
                            requestBaseQty=fullQty
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                            
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1 
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                        
                            if regularQty>0:                                                                        
                                short_note='Flat Rate balance regular rate, declared item'
                                promotion_type=''
                                bonus_applied_on_qty=0
                                circular_no=''
                                
                                #-----------
                                bonus_qty=0                            
                                totalAmountTP+=round(regularQty*price,6)
                                totalAmountVat+=round(regularQty*item_vat,6)
                                
                                #-----------
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:
                                    totalAmt+=round(regularQty*price,2)
                                    short_note='Flat Rate balance regular rate and applied regular discount'
                                    
                                #------------ set batch id after checking stock
                                requestBaseQty=regularQty
                                
                                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                                for stockRow in stockRows:
                                    batch_id=stockRow.batch_id
                                    quantity=stockRow.quantity
                                    block_qty=stockRow.block_qty
                                    availableQty=quantity-block_qty
                                    
                                    if requestBaseQty<=availableQty:
                                        newBlockQty=block_qty+requestBaseQty
                                        newBaseQty=requestBaseQty
                                        requestBaseQty=0
                                        
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)                        
                                        stockRow.update_record(block_qty=newBlockQty)                        
                                        break
                                    else:
                                        newBlockQty=block_qty+availableQty
                                        newBaseQty=availableQty
                                        requestBaseQty=requestBaseQty-availableQty
                                        
                                        #--------------
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)
                                        stockRow.update_record(block_qty=newBlockQty)
                                        
                                #--------------
                                if requestBaseQty>0:
                                    batch_id=''
                                    emptyBatchFlag=1
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    
                        #---------------------------------------    All quantity regular rate if minimum rate matching                        
                        else:                            
                            fullQty=item_qty_value
                            
                            newPrice=flat_rate                                               
                            short_note='Flat Rate applied'
                            promotion_type='FLAT'
                            bonus_applied_on_qty=0
                            circular_no=campaign_ref
                            
                            #-----------
                            bonus_qty=0
                            
                            totalAmountTP+=round(fullQty*newPrice,6)
                            totalAmountVat+=round(fullQty*item_vat,6)
                            
                            if regular_discount_apply=='YES': #apply for all qty
                                #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:
                                    discountRate=newPrice
                                    #regular rate, applied discount                                    
                                    totalAmt+=round(fullQty*discountRate,2)
                                    short_note+=' and regular discount'
                            
                            #------------ set batch id after checking stock
                            requestBaseQty=fullQty
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1 
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------
                        
                        promoFlag=1                        
                        ordRec.update_record(fr_flag=1)
                        break
            #-------- promo ref=1 then aproved rate later
            if promo_ref==1:
                #-------- step-1: Approved rate            
                ordRecords1=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)&(db.sm_tp_rules_temp_process_manual.fr_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
                for ordRec in ordRecords1:             
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    actual_tp=ordRec.actual_tp
                    actual_vat=ordRec.actual_vat
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)   
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton
                    
                    for appItemRow in approvedItemRows:
                        product_id=str(appItemRow.product_id).strip().upper()
                        bonus_type=appItemRow.bonus_type
                        fixed_percent_rate=appItemRow.fixed_percent_rate
                        
                        if product_id==item_id:
                            short_note=''
                            newPrice=0
                            promotion_type='APPROVED'
                            bonus_applied_on_qty=0
                            circular_no=''
                            
                            if bonus_type=='Fixed':
                                newPrice=fixed_percent_rate
                                short_note='Approved Fixed Rate '+str(newPrice)+',TP '+str(price)
                            elif bonus_type=='Percentage':
                                newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
                                short_note='Approved '+str(fixed_percent_rate)+'% of TP '+str(price)
                            #-----------
                            bonus_qty=0                        
                            totalAmountTP+=round(item_qty_value*newPrice,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)                
                            
                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                            
                            promoFlag=1                        
                            ordRec.update_record(ar_flag=1)
                            break
            
            #-------- step-5: Declared Item           
            ordRecords5=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)&(db.sm_tp_rules_temp_process_manual.fr_flag==0)&(db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.status=='ACTIVE')&(db.sm_tp_rules_temp_process_manual.item_id==db.sm_promo_declared_item.product_id)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRec in ordRecords5:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                
                short_note='Declared Item'
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #-----------
                bonus_qty=0
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)
                
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1 
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
                    
                #---------------------------------------                
                promoFlag=1                        
                ordRec.update_record(di_flag=1)
                
            #-------- step-6: Regular Discount            
            ordRec6Qset=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)&(db.sm_tp_rules_temp_process_manual.fr_flag==0)&(db.sm_tp_rules_temp_process_manual.di_flag==0))
            ordRec6Rows=ordRec6Qset.select(db.sm_tp_rules_temp_process_manual.quantity,db.sm_tp_rules_temp_process_manual.price,db.sm_tp_rules_temp_process_manual.item_vat)
            if ordRec6Rows:
                #totalAmt=0
                # for ordRec6Row in ordRec6Rows:
                #     quantity=ordRec6Row.quantity
                #     price=ordRec6Row.price
                #     #item_vat=ordRec6Row.item_vat
                #     totalAmt+=quantity*price
            # discount calculation
            # discountRows=db((db.sm_promo_regular_discount.cid==c_id)&(db.sm_promo_regular_discount.from_date<=orderDate)&(db.sm_promo_regular_discount.to_date>=orderDate) & (db.sm_promo_regular_discount.status=='ACTIVE')&(db.sm_promo_regular_discount.min_amount<=totalAmt)).select(db.sm_promo_regular_discount.discount_precent,orderby=~db.sm_promo_regular_discount.min_amount,limitby=(0,1))
            # if discountRows:
            #     discount_precent=discountRows[0].discount_precent
            #
            #     discount=round((totalAmt*discount_precent)/100,2)

                ordRecords6=ordRec6Qset.select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
                for ordRec in ordRecords6:
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    actual_tp=ordRec.actual_tp
                    actual_vat=ordRec.actual_vat
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton

                    short_note='Regular Discount'
                    promotion_type=''
                    bonus_applied_on_qty=0
                    circular_no=''

                    #-----------
                    bonus_qty=0
                    totalAmountTP+=round(item_qty_value*price,6)
                    totalAmountVat+=round(item_qty_value*item_vat,6)

                    #------------ set batch id after checking stock
                    requestBaseQty=item_qty_value

                    stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                    for stockRow in stockRows:
                        batch_id=stockRow.batch_id
                        quantity=stockRow.quantity
                        block_qty=stockRow.block_qty
                        availableQty=quantity-block_qty

                        if requestBaseQty<=availableQty:
                            newBlockQty=block_qty+requestBaseQty
                            newBaseQty=requestBaseQty
                            requestBaseQty=0

                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)
                            stockRow.update_record(block_qty=newBlockQty)
                            break
                        else:
                            newBlockQty=block_qty+availableQty
                            newBaseQty=availableQty
                            requestBaseQty=requestBaseQty-availableQty

                            #--------------
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)
                            stockRow.update_record(block_qty=newBlockQty)

                    #--------------
                    if requestBaseQty>0:
                        batch_id=''
                        emptyBatchFlag=1
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        
                    #---------------------------------------
                    promoFlag=1
                    ordRec.update_record(rd_flag=1)

            ###7 discount for all
            ordRec7Qset = db((db.sm_tp_rules_temp_process_manual.cid == c_id) & (
                        db.sm_tp_rules_temp_process_manual.depot_id == depot_id) & (
                                         db.sm_tp_rules_temp_process_manual.sl == invoice_sl))
            ordRec7Rows = ordRec7Qset.select(db.sm_tp_rules_temp_process_manual.quantity,
                                             db.sm_tp_rules_temp_process_manual.price,
                                             db.sm_tp_rules_temp_process_manual.item_vat)
            if ordRec7Rows:
                totalAmt = 0
                for ordRec7Row in ordRec7Rows:
                    quantity = ordRec7Row.quantity
                    price = ordRec7Row.price
                    # item_vat=ordRec6Row.item_vat
                    totalAmt += quantity * price
            # discount calculation
            discountRows = db(
                (db.sm_promo_regular_discount.cid == c_id) & (db.sm_promo_regular_discount.from_date <= orderDate) & (
                            db.sm_promo_regular_discount.to_date >= orderDate) & (
                            db.sm_promo_regular_discount.status == 'ACTIVE') & (
                            db.sm_promo_regular_discount.min_amount <= totalAmt)).select(
                db.sm_promo_regular_discount.discount_precent, orderby=~db.sm_promo_regular_discount.min_amount,
                limitby=(0, 1))
            if discountRows:
                discount_precent = discountRows[0].discount_precent

                discount = round((totalAmt * discount_precent) / 100, 2)


            #------------ step-Last
            ordRecordsLast=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)&(db.sm_tp_rules_temp_process_manual.fr_flag==0)&(db.sm_tp_rules_temp_process_manual.di_flag==0)&(db.sm_tp_rules_temp_process_manual.rd_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRec in ordRecordsLast:
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)   
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                            
                bonus_qty=0                
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)            
                short_note='-'
                
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'category_id':category_id,'quantity':item_qty_value,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'note':req_note,'short_note':short_note,'status':'Submitted'}
                #detailList.append(detailDict)
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)                        
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        stockRow.update_record(block_qty=newBlockQty)
                        
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
                    
                #---------------------------------------
                
    discount=round(float(discount),2)
    totalAmount=(round(totalAmountTP,2)+round(totalAmountVat,2)-discount)
    
    sp_discount=round(float(sp_discount),2)
    
    retMsg=''
    #=============== Insert invoice head and details
    if (len(headList)> 0 and len(detailList) > 0):
        
        #----------- check credit policy
        limitOverFlag=0
        acknowledge_flag=0
        if payment_mode!='CASH':
            acknowledge_flag=1
            creditPolicyRow=db((db.sm_cp_approved.cid==c_id)&(db.sm_cp_approved.client_id==client_id)&(db.sm_cp_approved.status=='ACTIVE')).select(db.sm_cp_approved.credit_amount,limitby=(0,1))
            if not creditPolicyRow:
                limitOverFlag=1
            else:
                credit_amount=creditPolicyRow[0].credit_amount
                
                tx_closing_balance=0
                ledgerRow=db((db.sm_transaction.cid==c_id)&(db.sm_transaction.tx_account=='CLT-'+str(client_id))&(db.sm_transaction.opposite_account=='DPT-'+str(depot_id))).select(db.sm_transaction.tx_closing_balance,orderby=~db.sm_transaction.tx_date,limitby=(0,1))
                if ledgerRow:
                    tx_closing_balance=ledgerRow[0].tx_closing_balance            
                clientTotal=tx_closing_balance+totalAmount
                
                if clientTotal>credit_amount:
                    limitOverFlag=1
                    
        #----------- end check credit policy
        
        level0_id=''
        level0_name=''
        level1_id=''
        level1_name=''
        level2_id=''
        level2_name=''
        level3_id=''
        level3_name=''
        orderHRow=db((db.sm_invoice_head.cid==c_id) & (db.sm_invoice_head.depot_id==depot_id) &(db.sm_invoice_head.sl==invoice_sl)).select(db.sm_invoice_head.level0_id,db.sm_invoice_head.level0_name,db.sm_invoice_head.level1_id,db.sm_invoice_head.level1_name,db.sm_invoice_head.level2_id,db.sm_invoice_head.level2_name,db.sm_invoice_head.level3_id,db.sm_invoice_head.level3_name,limitby=(0,1))
        if orderHRow:
            level0_id=orderHRow[0].level0_id
            level0_name=orderHRow[0].level0_name
            level1_id=orderHRow[0].level1_id
            level1_name=orderHRow[0].level1_name
            level2_id=orderHRow[0].level2_id
            level2_name=orderHRow[0].level2_name
            level3_id=orderHRow[0].level3_id
            level3_name=orderHRow[0].level3_name
            
        #---------- dicount amount assigned
        for i in range(len(headList)):
            headDictData=headList[i]
            headDictData['discount']=discount
            headDictData['client_limit_over']=limitOverFlag
            headDictData['empty_batch_flag']=emptyBatchFlag
            headDictData['acknowledge_flag']=acknowledge_flag
            headDictData['level0_id']=level0_id
            headDictData['level0_name']=level0_name
            headDictData['level1_id']=level1_id
            headDictData['level1_name']=level1_name
            headDictData['level2_id']=level2_id
            headDictData['level2_name']=level2_name
            headDictData['level3_id']=level3_id
            headDictData['level3_name']=level3_name
            headDictData['discount_precent']=discount_precent
            headDictData['sp_discount']=sp_discount
            
        for j in range(len(detailList)):
            detailDictData=detailList[j]
            detailDictData['discount']=discount
            detailDictData['level0_id']=level0_id
            detailDictData['level0_name']=level0_name
            detailDictData['level1_id']=level1_id
            detailDictData['level1_name']=level1_name
            detailDictData['level2_id']=level2_id
            detailDictData['level2_name']=level2_name
            detailDictData['level3_id']=level3_id
            detailDictData['level3_name']=level3_name
            
        #-------------
        #Update status of head and detail       
        
        db((db.sm_invoice_head.cid==c_id) & (db.sm_invoice_head.depot_id==depot_id) &(db.sm_invoice_head.sl==invoice_sl)).delete()
        db((db.sm_invoice.cid==c_id) & (db.sm_invoice.depot_id==depot_id) &(db.sm_invoice.sl==invoice_sl)).delete()
        
        rows=db.sm_invoice.bulk_insert(detailList)
        rows=db.sm_invoice_head.bulk_insert(headList)                        
        
        retMsg='Processed Successfully '
        db.commit()
        
    #-------------- end order
    
    return retMsg


#***** new invoice with promotion and credit limit
# change:- parameter, insert into temp, sm_tp_rules_temp_process->sm_tp_rules_temp_process_manual, order_sl->invoice_sl

def get_order_to_delivery_detail_rules_manual_with_rd(cid,depot_id,invoice_sl,order_sl,clientId,orderDate):
    c_id=cid
    depot_id=depot_id
    sl=order_sl
    client_id=clientId
    orderDate=orderDate #Q? it is current date or order date, now orderDate used?
    
    #------------  insert into temp
    # Head Loop
    
    promo_ref=0
    
    invoiceHeadRecords=db((db.sm_invoice_head.cid==c_id)&(db.sm_invoice_head.depot_id==depot_id)&(db.sm_invoice_head.sl==invoice_sl)&(db.sm_invoice_head.status=='Draft')).select(db.sm_invoice_head.ALL,limitby=(0,1))
    if not invoiceHeadRecords:
        return 'Invalid request'
    else:
        depot_id=invoiceHeadRecords[0].depot_id
        depot_name=invoiceHeadRecords[0].depot_name
        store_id=invoiceHeadRecords[0].store_id
        store_name=invoiceHeadRecords[0].store_name
        
        client_name=invoiceHeadRecords[0].client_name
        rep_id=invoiceHeadRecords[0].rep_id
        rep_name=invoiceHeadRecords[0].rep_name
        order_date=invoiceHeadRecords[0].order_datetime#order_date
        order_datetime=invoiceHeadRecords[0].order_datetime
        delivery_date=invoiceHeadRecords[0].delivery_date
        payment_mode=invoiceHeadRecords[0].payment_mode
        area_id=invoiceHeadRecords[0].area_id
        area_name=invoiceHeadRecords[0].area_name
        order_media=invoiceHeadRecords[0].invoice_media
        ym_date=invoiceHeadRecords[0].ym_date
        client_cat=''#invoiceHeadRecords[0].client_cat
        note=invoiceHeadRecords[0].note
        market_id=invoiceHeadRecords[0].market_id
        market_name=invoiceHeadRecords[0].market_name
        
        promo_ref=invoiceHeadRecords[0].promo_ref  
        if promo_ref!=0:
            promo_ref=1
                
        orderRows=db((db.sm_invoice.cid==c_id) & (db.sm_invoice.depot_id==depot_id)&(db.sm_invoice.sl==invoice_sl)).select(db.sm_invoice.ALL,orderby=db.sm_invoice.item_id)
        detailList=[]
        for ordRow in orderRows:
            item_id=str(ordRow.item_id).strip().upper()
            item_name=ordRow.item_name
            category_id=ordRow.category_id
            actual_tp=ordRow.actual_tp
            actual_vat=ordRow.actual_vat
            quantity=ordRow.quantity
            price=ordRow.price
            item_vat=ordRow.item_vat
            item_unit=ordRow.item_unit
            item_carton=ordRow.item_carton
            sp_discount_item=ordRow.sp_discount_item
            
            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':invoice_sl,'store_id':store_id,'store_name':store_name,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'order_date':order_date,'order_datetime':order_datetime,'delivery_date':delivery_date,
                        'payment_mode':payment_mode,'area_id':area_id,'area_name':area_name,'order_media':order_media,'ym_date':ym_date,'client_cat':client_cat,'note':note,'item_id':item_id,'item_name':item_name,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':quantity,'price':price,'item_vat':item_vat,'item_unit':item_unit,'item_carton':item_carton}
            detailList.append(detailDict)
            
        #delete temp
        db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)).delete()
        
        #insert temp
        db.sm_tp_rules_temp_process_manual.bulk_insert(detailList)
        
    #========================-get settings flag
    invoiceRulesFlag=False
    
    compSttRows=db((db.sm_settings.cid==c_id)&(db.sm_settings.s_key=='INVOICE_RULES')&(db.sm_settings.s_value=='YES')).select(db.sm_settings.cid,limitby=(0,1))
    if compSttRows:
        invoiceRulesFlag=True
        
    #================ if invoice rules are to apply (Note: ANY or Sepcific item, at a time two rules not applicable)
    productBonusPriorityRows=''
    approvedItemRows=''    
    productBonusRows=''
    specialRateRows=''
    flatRateRows=''
    
    if invoiceRulesFlag==True:
        approvedItemRows=db((db.sm_promo_approved_rate.cid==c_id)&(db.sm_promo_approved_rate.client_id==client_id)&(db.sm_promo_approved_rate.from_date<=orderDate)&(db.sm_promo_approved_rate.to_date>=orderDate)&(db.sm_promo_approved_rate.status=='ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date|db.sm_promo_approved_rate.product_id)
        productBonusRows=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,db.sm_promo_product_bonus.until_stock_last,db.sm_promo_product_bonus.allowed_credit_inv,db.sm_promo_product_bonus.regular_discount_apply,orderby=~db.sm_promo_product_bonus.min_qty)       #&(db.sm_promo_product_bonus.id!=promo_ref)
        specialRateRows=db((db.sm_promo_special_rate.cid==c_id)&(db.sm_promo_special_rate.from_date<=orderDate)&(db.sm_promo_special_rate.to_date>=orderDate)&(db.sm_promo_special_rate.status=='ACTIVE')).select(db.sm_promo_special_rate.product_id,db.sm_promo_special_rate.min_qty,db.sm_promo_special_rate.special_rate_tp,db.sm_promo_special_rate.special_rate_vat,db.sm_promo_special_rate.allowed_credit_inv,db.sm_promo_special_rate.regular_discount_apply,orderby=~db.sm_promo_special_rate.from_date)
        flatRateRows=db((db.sm_promo_flat_rate.cid==c_id)&(db.sm_promo_flat_rate.from_date<=orderDate)&(db.sm_promo_flat_rate.to_date>=orderDate)&(db.sm_promo_flat_rate.status=='ACTIVE')).select(db.sm_promo_flat_rate.campaign_ref,db.sm_promo_flat_rate.product_id,db.sm_promo_flat_rate.min_qty,db.sm_promo_flat_rate.flat_rate,db.sm_promo_flat_rate.allowed_credit_inv,db.sm_promo_flat_rate.regular_discount_apply,db.sm_promo_flat_rate.allow_bundle,orderby=~db.sm_promo_flat_rate.from_date)

        # common approved rate
        #approvedItemRows = db((db.sm_promo_approved_rate.cid == c_id) & (db.sm_promo_approved_rate.from_date <= orderDate) & (db.sm_promo_approved_rate.to_date >= orderDate) & (db.sm_promo_approved_rate.status == 'ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date | db.sm_promo_approved_rate.product_id)

    #----------- 
    maxSl=invoice_sl
    
    records=''
    #---------------   order detail records
    depot_name=''    
    client_name=''
    rep_id=''
    rep_name=''
    area_id=''
    area_name=''
    order_datetime=''
    payment_mode=''
    req_note=''
    ym_date=''
    req_delivery_date=''
    
    #----------------
    headList=[]                                               
    detailDict={}
    detailList=[]                            
    headFlag=False
    
    totalAmountTP=0
    totalAmountVat=0
    discount=0
    sp_discount=0 
    discount_precent=0
    #order details loop      
    orderRecords=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)).select(db.sm_tp_rules_temp_process_manual.ALL,limitby=(0,1))
    if orderRecords:
        depot_name=orderRecords[0].depot_name
        store_id=orderRecords[0].store_id
        store_name=orderRecords[0].store_name
        client_id=orderRecords[0].client_id
        client_name=orderRecords[0].client_name
        clientCategory=orderRecords[0].client_cat
        rep_id=orderRecords[0].rep_id
        rep_name=orderRecords[0].rep_name
        area_id=orderRecords[0].area_id
        area_name=orderRecords[0].area_name                                
        order_datetime=orderRecords[0].order_datetime
        order_media=orderRecords[0].order_media
        delivery_date=orderRecords[0].delivery_date
        payment_mode=orderRecords[0].payment_mode
        req_note=orderRecords[0].note
        market_id=orderRecords[0].market_id
        market_name=orderRecords[0].market_name
        
        #---delivery date get from order date
        ym_date=str(delivery_date)[0:7]+'-01'
        req_delivery_date=str(delivery_date)[0:10]
        
        #head records
        headDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'store_id':store_id,'store_name':store_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,'invoice_media':order_media,'area_id':area_id,'area_name':area_name,'status':'Submitted','ym_date':ym_date,'promo_ref':promo_ref}
        headList.append(headDict)
        
        emptyBatchFlag=0
        if invoiceRulesFlag==False:
            #=========================== Rules not apply
            ordRecords=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRecord in ordRecords:
                item_id=str(ordRecord.item_id).strip().upper()
                item_name=ordRecord.item_name
                category_id=ordRecord.category_id
                actual_tp=ordRecord.actual_tp
                actual_vat=ordRecord.actual_vat
                item_qty_value=int(ordRecord.quantity)
                price=float(ordRecord.price)   
                item_vat=float(ordRecord.item_vat)
                item_unit=ordRecord.item_unit
                item_carton=ordRecord.item_carton
                
                #-----------
                bonus_qty=0
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)
                short_note=''
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)                        
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        stockRow.update_record(block_qty=newBlockQty)
                        
                    
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
                    
        else:
            #===================== Rules apply 
            promoFlag=0
            totalAmt=0
            
            #-------- step-0: Priority (Product Bonus) 
            
            if promo_ref==0:
                #-------- step-1: Approved rate            
                ordRecords1=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
                for ordRec in ordRecords1:             
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    actual_tp=ordRec.actual_tp
                    actual_vat=ordRec.actual_vat
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)   
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton
                
                    for appItemRow in approvedItemRows:
                        product_id=str(appItemRow.product_id).strip().upper()
                        bonus_type=appItemRow.bonus_type
                        fixed_percent_rate=appItemRow.fixed_percent_rate
                        
                        if product_id==item_id:
                            short_note=''
                            newPrice=0
                            promotion_type='APPROVED'
                            bonus_applied_on_qty=0
                            circular_no=''
                            
                            if bonus_type=='Fixed':
                                newPrice=fixed_percent_rate
                                short_note='Approved Fixed Rate '+str(newPrice)+',TP '+str(price)
                            elif bonus_type=='Percentage':
                                newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
                                short_note='Approved '+str(fixed_percent_rate)+'% of TP '+str(price)
                            #-----------
                            bonus_qty=0                        
                            totalAmountTP+=round(item_qty_value*newPrice,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)                
                                                    
                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                            
                            promoFlag=1                        
                            ordRec.update_record(ar_flag=1)
                            break
            
            #-------- step-2: Product Bonus
            for prodBonusRow in productBonusRows:      
                rowid=prodBonusRow.id
                circular_number=prodBonusRow.circular_number
                min_qty=prodBonusRow.min_qty
                #until_stock_last=str(prodBonusRow.until_stock_last).strip().upper()          #for bonus
                allowed_credit_inv=str(prodBonusRow.allowed_credit_inv).strip().upper()      #for bonus
                regular_discount_apply=str(prodBonusRow.regular_discount_apply).strip().upper()  #for product full qty
                
                allowBonus='YES'
                if payment_mode!='CASH':
                    if allowed_credit_inv=='NO':
                        allowBonus='NO'
                
                if allowBonus=='NO':
                    continue
                    
                pbQset=db((db.sm_promo_product_bonus_products.cid==c_id)&(db.sm_promo_product_bonus_products.refrowid==rowid)&(db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_promo_product_bonus_products.product_id==db.sm_tp_rules_temp_process_manual.item_id))
                totalQtyRows=pbQset.select(db.sm_tp_rules_temp_process_manual.quantity.sum(),groupby=db.sm_tp_rules_temp_process_manual.cid)
                
                if totalQtyRows:
                    qtyCount=totalQtyRows[0][db.sm_tp_rules_temp_process_manual.quantity.sum()]
                    
                    if qtyCount>=min_qty:                        
                        fullCount=int(qtyCount/min_qty)
                        
                        #===================================== for bonus calculate
                        circularStr=circular_number
                        
                        nextQtyCount=qtyCount-min_qty*fullCount
                        
                        regularQty=0       #extra Qty
                        discountRate=0
                        
                        itemFullQty=min_qty*fullCount
                        
                        bonusDictList=[]
                        bonusDictList.append({'rowid':rowid,'fullCount':fullCount,'circularNo':circular_number})
                        
                        if nextQtyCount>0:
                            prodPromList=[]
                            totalItemRows=pbQset.select(db.sm_tp_rules_temp_process_manual.item_id,groupby=db.sm_tp_rules_temp_process_manual.item_id)
                            for totItemRow in totalItemRows:                            
                                prodPromList.append(totItemRow.item_id)
                                
                            productBonusRows2=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')&(db.sm_promo_product_bonus.id!=rowid)&(db.sm_promo_product_bonus.id==db.sm_promo_product_bonus_products.refrowid)&(db.sm_promo_product_bonus_products.product_id.belongs(prodPromList))).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,orderby=~db.sm_promo_product_bonus.min_qty,groupby=db.sm_promo_product_bonus.id)
                            if productBonusRows2:                            
                                for productBonusRow2 in productBonusRows2:      
                                    rowid2=productBonusRow2.id
                                    circular_number2=productBonusRow2.circular_number
                                    min_qty2=productBonusRow2.min_qty
                                    
                                    if nextQtyCount>=min_qty2:
                                        fullCount2=int(nextQtyCount/min_qty2)
                                        
                                        circularStr+=','+str(circular_number2)
                                        bonusDictList.append({'rowid':rowid2,'fullCount':fullCount2,'circularNo':circular_number2})
                                        
                                        nextQtyCount=nextQtyCount-min_qty2*fullCount2
                                        itemFullQty+=min_qty2*fullCount2
                                              
                                    else:                                        
                                        break
                                        
                                if nextQtyCount>0:
                                    regularQty=nextQtyCount
                                    #discount apply
                            else:
                                regularQty=nextQtyCount
                                #discount apply
                        
                        #----------------                        
                        bonusStockFlag='YES'
                        bonusItemList=[]                        
                        #--------- bonus item qty available check                        
                        for k in range(len(bonusDictList)):
                            bonusDictData=bonusDictList[k]                            
                            bRowid=bonusDictData['rowid']
                            bfullCount=bonusDictData['fullCount']
                            
                            bonusRows=db((db.sm_promo_product_bonus_bonuses.cid==c_id)&(db.sm_promo_product_bonus_bonuses.refrowid==bRowid)).select(db.sm_promo_product_bonus_bonuses.bonus_product_id,db.sm_promo_product_bonus_bonuses.bonus_qty)
                            for bonusRow in bonusRows:
                                item_id=bonusRow.bonus_product_id                                
                                bonus_qty=bonusRow.bonus_qty*bfullCount                                
                                get_index=-1
                                try:
                                    get_index=map(itemgetter('item_id'), bonusItemList).index(item_id)    
                                except:
                                    get_index=-1                   
                                    
                                if get_index==-1:
                                    bonusItemList.append({'item_id':item_id,'item_qty':bonus_qty})                                
                                else:      
                                    for z in range(len(bonusItemList)):
                                        bonusItemData=bonusItemList[z]
                                        bonusItemId=bonusItemData['item_id']
                                        bonusItemQty=bonusItemData['item_qty']                                        
                                        if bonusItemId==item_id:
                                            bonusItemData['item_qty']=int(bonus_qty+bonusItemQty)
                                            break
                        
                        #--------- bonus item qty available check                        
                        for m in range(len(bonusItemList)):
                            b_bonusDictData=bonusItemList[m]                            
                            b_item_id=b_bonusDictData['item_id']
                            b_item_qty=b_bonusDictData['item_qty']
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==b_item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.quantity.sum(),db.sm_depot_stock_balance.block_qty.sum(),groupby=db.sm_depot_stock_balance.item_id)
                            if stockRows:
                                for stockRow in stockRows:
                                    quantity=stockRow[db.sm_depot_stock_balance.quantity.sum()]
                                    block_qty=stockRow[db.sm_depot_stock_balance.block_qty.sum()]
                                    availableQty=quantity-block_qty
                                    if b_item_qty>availableQty:
                                        bonusStockFlag='NO'
                                        break
                                if bonusStockFlag=='NO':
                                    break
                            else:
                                bonusStockFlag='NO'
                                break
                                
                        if bonusStockFlag=='NO':
                            regular_discount_apply='YES'    #regular discount for all items
                            
                        #------ insert and update flag
                        regularQtyDisFlag='YES'
                        bonusOnQty=itemFullQty
                        regularQtyAmt=0
                        
                        ordRecords2=pbQset.select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
                        for ordRec in ordRecords2:
                            item_id=str(ordRec.item_id).strip().upper()
                            item_name=ordRec.item_name
                            category_id=ordRec.category_id
                            actual_tp=ordRec.actual_tp
                            actual_vat=ordRec.actual_vat
                            item_qty_value=int(ordRec.quantity)
                            price=float(ordRec.price)   
                            item_vat=float(ordRec.item_vat)
                            item_unit=ordRec.item_unit
                            item_carton=ordRec.item_carton
                            
                            #------------------
                            discount_rate=price
                            
                            specialNote=''                        
                            for spRateRow in specialRateRows:
                                product_id=str(spRateRow.product_id).strip().upper()
                                minQty=spRateRow.min_qty
                                special_rate_tp=spRateRow.special_rate_tp
                                special_rate_vat=spRateRow.special_rate_vat                                
                                allowed_credit_inv=str(spRateRow.allowed_credit_inv).strip().upper()                                
                                if product_id==item_id:
                                    allowSpecialRate='YES'
                                    if payment_mode!='CASH':
                                        if allowed_credit_inv=='NO':
                                            allowSpecialRate='NO'                        
                                    
                                    #check special rate applicable                                    
                                    if allowSpecialRate=='NO':
                                        price=special_rate_tp
                                        item_vat=special_rate_vat
                                        regular_discount_apply='YES'            
                                        specialNote=' with special Rate (Premium TP) and vat applied'                                    
                                        actual_tp=special_rate_tp
                                        actual_vat=special_rate_vat
                                        break
                                    else:
                                        if item_qty_value<minQty:                                    
                                            price=special_rate_tp
                                            item_vat=special_rate_vat
                                            regular_discount_apply='YES'              
                                            specialNote=' with special Rate (Premium TP) and vat applied'                                    
                                            actual_tp=special_rate_tp
                                            actual_vat=special_rate_vat
                                            break
                                        else:
                                            regular_discount_apply='NO'
                                            regularQtyDisFlag='NO'
                                            break
                            #-----------
                            bonus_qty=0
                            totalAmountTP+=round(item_qty_value*price,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)
                            short_note='Bonus apply, Circular '+str(circularStr)+str(specialNote)
                            
                            regQty=0
                            promotion_type='BONUS'                            
                            if bonusOnQty>item_qty_value:
                                bonus_applied_on_qty=item_qty_value
                                bonusOnQty=bonusOnQty-item_qty_value                                
                            else:
                                bonus_applied_on_qty=bonusOnQty
                                
                                regQty=int(item_qty_value-bonusOnQty)
                                bonusOnQty=0
                            
                            circular_no=str(circularStr)
                            
                            #----------- new code
                            declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                            if not declaredItemRow:
                                discountRate=discount_rate
                                #regular rate, applied discount
                                
                                if regular_discount_apply=='YES': #apply for all qty
                                    totalAmt+=round(item_qty_value*price,2)
                                    short_note+=' and regular discount'
                                else:
                                    if regularQty>0 and regQty>0:
                                        if regularQtyDisFlag=='YES':
                                            #short_note+=' and regular discount on '+str(regularQty)+' Quantity'
                                            short_note+=' and regular discount on '+str(regQty)+' Quantity'
                                            regularQtyAmt+=regQty*price
                                            
                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                            
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1           
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                            
                            promoFlag=1                            
                            ordRec.update_record(pb_flag=1)
                            
                        if regular_discount_apply!='YES': #apply for all qty
                            #new code
                            #product bonus rest qty discount apply       
                            if regularQtyDisFlag=='YES':
                                #totalAmt+=round(regularQty*discountRate,2)
                                totalAmt+=round(regularQtyAmt,2)
                                
                        if bonusStockFlag=='YES':
                            #--------- bonus item insert                        
                            for k in range(len(bonusDictList)):
                                bonusDictData=bonusDictList[k]
                                
                                bRowid=bonusDictData['rowid']
                                bfullCount=bonusDictData['fullCount']
                                bcircularNo=bonusDictData['circularNo']
                                #end new code next use bRowid
                                
                                #--------- bonus item add
                                bonusRows=db((db.sm_promo_product_bonus_bonuses.cid==c_id)&(db.sm_promo_product_bonus_bonuses.refrowid==bRowid)&(db.sm_item.cid==c_id)&(db.sm_item.item_id==db.sm_promo_product_bonus_bonuses.bonus_product_id)).select(db.sm_promo_product_bonus_bonuses.bonus_product_id,db.sm_item.name,db.sm_item.category_id,db.sm_item.category_id_sp,db.sm_item.unit_type,db.sm_item.item_carton,db.sm_promo_product_bonus_bonuses.bonus_qty)
                                for bonusRow in bonusRows:
                                    bonus_product_id=bonusRow.sm_promo_product_bonus_bonuses.bonus_product_id
                                    bonus_product_name=bonusRow.sm_item.name
                                    bonus_product_category_id=bonusRow.sm_item.category_id
                                    bonus_product_category_id_sp=bonusRow.sm_item.category_id_sp
                                    bonus_item_qty=bonusRow.sm_promo_product_bonus_bonuses.bonus_qty                            
                                    bonus_product_unit_type=bonusRow.sm_item.unit_type
                                    bonus_product_item_carton=bonusRow.sm_item.item_carton
                                    actual_tp=0
                                    actual_vat=0
                                    #----
                                    item_id=bonus_product_id
                                    item_name=bonus_product_name
                                    category_id=bonus_product_category_id
                                    item_qty_value=0
                                    bonus_qty=bonus_item_qty*bfullCount
                                    newPrice=0
                                    item_vat=0
                                    item_unit=bonus_product_unit_type
                                    item_carton=bonus_product_item_carton
                                    
                                    short_note='Bonus Item, Circular '+str(bcircularNo)
                                    promotion_type=''
                                    bonus_applied_on_qty=0
                                    circular_no=str(bcircularNo)
                                    
                                    #------------ set batch id after checking stock
                                    requestBaseQty=bonus_qty
                                    
                                    stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                                    for stockRow in stockRows:
                                        batch_id=stockRow.batch_id
                                        quantity=stockRow.quantity
                                        block_qty=stockRow.block_qty
                                        availableQty=quantity-block_qty
                                        
                                        if requestBaseQty<=availableQty:
                                            newBlockQty=block_qty+requestBaseQty
                                            newBaseQty=requestBaseQty
                                            requestBaseQty=0
                                            
                                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':newBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                            detailList.append(detailDict)                        
                                            stockRow.update_record(block_qty=newBlockQty)                        
                                            break
                                        else:
                                            newBlockQty=block_qty+availableQty
                                            newBaseQty=availableQty
                                            requestBaseQty=requestBaseQty-availableQty
                                            
                                            #--------------
                                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':newBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                            detailList.append(detailDict)
                                            stockRow.update_record(block_qty=newBlockQty)
                                     
                                    #--------------
                                    #if until_stock_last=='NA':# Until last stock available
                                    if requestBaseQty>0:
                                        batch_id=''
                                        emptyBatchFlag=1
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':item_qty_value,'bonus_qty':requestBaseQty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)
                                    
                                    #---------------------------------------                                
                                    promoFlag=1
                    
                    #------------
            
            #-------- step-3: Special rate            
            ordRecords3=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRec in ordRecords3:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                
                for spRateRow in specialRateRows:
                    product_id=str(spRateRow.product_id).strip().upper()
                    min_qty=spRateRow.min_qty
                    special_rate_tp=spRateRow.special_rate_tp
                    special_rate_vat=spRateRow.special_rate_vat
                    
                    allowed_credit_inv=str(spRateRow.allowed_credit_inv).strip().upper()
                    regular_discount_apply=str(spRateRow.regular_discount_apply).strip().upper()
                    
                    if product_id==item_id:
                        allowSpecialRate='YES'
                        if payment_mode!='CASH':
                            if allowed_credit_inv=='NO':
                                allowSpecialRate='NO'                        
                        
                        #check special rate applicable        
                        promotion_type=''
                        bonus_applied_on_qty=0
                        circular_no=''                
                        if allowSpecialRate=='NO':
                            newPrice=special_rate_tp
                            regular_discount_apply='YES'
                            short_note='Special Rate (Premium TP) and vat applied'
                            actual_tp=special_rate_tp
                            actual_vat=special_rate_vat                            
                        else:
                            if item_qty_value<min_qty:
                                newPrice=special_rate_tp
                                regular_discount_apply='YES'
                                short_note='Special Rate (Premium TP) and vat applied'                            
                                actual_tp=special_rate_tp
                                actual_vat=special_rate_vat                            
                            else:
                                newPrice=price
                                regular_discount_apply='NO'
                                short_note='Special Rate and vat applied'
                        
                        newVat=special_rate_vat 
                        
                        #-----------
                        bonus_qty=0                        
                        totalAmountTP+=round(item_qty_value*newPrice,6)
                        totalAmountVat+=round(item_qty_value*newVat,6)
                        
                        if regular_discount_apply=='YES': #apply for all qty
                            #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                            declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                            if not declaredItemRow:                                                                       
                                totalAmt+=round(item_qty_value*newPrice,2)                                    
                                short_note+=' and regular discount'
                                
                        #------------ set batch id after checking stock
                        requestBaseQty=item_qty_value
                        
                        stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                        for stockRow in stockRows:
                            batch_id=stockRow.batch_id
                            quantity=stockRow.quantity
                            block_qty=stockRow.block_qty
                            availableQty=quantity-block_qty
                            
                            if requestBaseQty<=availableQty:
                                newBlockQty=block_qty+requestBaseQty
                                newBaseQty=requestBaseQty
                                requestBaseQty=0
                                
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)                        
                                stockRow.update_record(block_qty=newBlockQty)                        
                                break
                            else:
                                newBlockQty=block_qty+availableQty
                                newBaseQty=availableQty
                                requestBaseQty=requestBaseQty-availableQty
                                
                                #--------------
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                stockRow.update_record(block_qty=newBlockQty)
                        
                        #--------------
                        if requestBaseQty>0:
                            batch_id=''
                            emptyBatchFlag=1
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)
                            
                        #---------------------------------------                        
                        promoFlag=1                        
                        ordRec.update_record(sr_flag=1)
                        break
                        
            #-------- step-4: Flat rate            
            ordRecords4=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRec in ordRecords4:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                            
                for flatRateRow in flatRateRows:
                    campaign_ref=str(flatRateRow.campaign_ref).strip()
                    product_id=str(flatRateRow.product_id).strip().upper()
                    min_qty=flatRateRow.min_qty
                    flat_rate=flatRateRow.flat_rate
                    
                    allowed_credit_inv=str(flatRateRow.allowed_credit_inv).strip().upper()
                    regular_discount_apply=str(flatRateRow.regular_discount_apply).strip().upper()
                    allow_bundle=str(flatRateRow.allow_bundle).strip().upper()  #for different processing rules
                    
                    if product_id==item_id and item_qty_value>=min_qty:
                        allowFlatRate='YES'
                        if payment_mode!='CASH':
                            if allowed_credit_inv=='NO':
                                allowFlatRate='NO'
                        
                        #check flat rate applicable
                        if allowFlatRate=='NO':
                            break
                            
                        #------------------------------Allow per bundle calculated and extra will be regular rate
                        if allow_bundle=='YES':                        
                            regularQty=(item_qty_value%min_qty)
                            fullQty=item_qty_value-regularQty
                            
                            newPrice=flat_rate                                               
                            short_note='Flat Rate applied'
                            promotion_type='FLAT'
                            bonus_applied_on_qty=0
                            circular_no=campaign_ref
                            
                            #-----------
                            bonus_qty=0
                            
                            totalAmountTP+=round(fullQty*newPrice,6)
                            totalAmountVat+=round(fullQty*item_vat,6)
                            
                            if regular_discount_apply=='YES': #apply for all qty
                                #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:                                                                       
                                    totalAmt+=round(fullQty*newPrice,2)                                    
                                    short_note+=' and regular discount'
                            
                            #------------ set batch id after checking stock
                            requestBaseQty=fullQty
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                            
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1 
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                        
                            if regularQty>0:                                                                        
                                short_note='Flat Rate balance regular rate, declared item'
                                promotion_type=''
                                bonus_applied_on_qty=0
                                circular_no=''
                                
                                #-----------
                                bonus_qty=0                            
                                totalAmountTP+=round(regularQty*price,6)
                                totalAmountVat+=round(regularQty*item_vat,6)
                                
                                #-----------
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:
                                    totalAmt+=round(regularQty*price,2)
                                    short_note='Flat Rate balance regular rate and applied regular discount'
                                    
                                #------------ set batch id after checking stock
                                requestBaseQty=regularQty
                                
                                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                                for stockRow in stockRows:
                                    batch_id=stockRow.batch_id
                                    quantity=stockRow.quantity
                                    block_qty=stockRow.block_qty
                                    availableQty=quantity-block_qty
                                    
                                    if requestBaseQty<=availableQty:
                                        newBlockQty=block_qty+requestBaseQty
                                        newBaseQty=requestBaseQty
                                        requestBaseQty=0
                                        
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)                        
                                        stockRow.update_record(block_qty=newBlockQty)                        
                                        break
                                    else:
                                        newBlockQty=block_qty+availableQty
                                        newBaseQty=availableQty
                                        requestBaseQty=requestBaseQty-availableQty
                                        
                                        #--------------
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                        detailList.append(detailDict)
                                        stockRow.update_record(block_qty=newBlockQty)
                                        
                                #--------------
                                if requestBaseQty>0:
                                    batch_id=''
                                    emptyBatchFlag=1
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    
                        #---------------------------------------    All quantity regular rate if minimum rate matching                        
                        else:                            
                            fullQty=item_qty_value
                            
                            newPrice=flat_rate                                               
                            short_note='Flat Rate applied'
                            promotion_type='FLAT'
                            bonus_applied_on_qty=0
                            circular_no=campaign_ref
                            
                            #-----------
                            bonus_qty=0
                            
                            totalAmountTP+=round(fullQty*newPrice,6)
                            totalAmountVat+=round(fullQty*item_vat,6)
                            
                            if regular_discount_apply=='YES': #apply for all qty
                                #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:
                                    discountRate=newPrice
                                    #regular rate, applied discount                                    
                                    totalAmt+=round(fullQty*discountRate,2)
                                    short_note+=' and regular discount'
                            
                            #------------ set batch id after checking stock
                            requestBaseQty=fullQty
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1 
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------
                        
                        promoFlag=1                        
                        ordRec.update_record(fr_flag=1)
                        break
            #-------- promo ref=1 then aproved rate later
            if promo_ref==1:
                #-------- step-1: Approved rate            
                ordRecords1=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)&(db.sm_tp_rules_temp_process_manual.fr_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
                for ordRec in ordRecords1:             
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    actual_tp=ordRec.actual_tp
                    actual_vat=ordRec.actual_vat
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)   
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton
                    
                    for appItemRow in approvedItemRows:
                        product_id=str(appItemRow.product_id).strip().upper()
                        bonus_type=appItemRow.bonus_type
                        fixed_percent_rate=appItemRow.fixed_percent_rate
                        
                        if product_id==item_id:
                            short_note=''
                            newPrice=0
                            promotion_type='APPROVED'
                            bonus_applied_on_qty=0
                            circular_no=''
                            
                            if bonus_type=='Fixed':
                                newPrice=fixed_percent_rate
                                short_note='Approved Fixed Rate '+str(newPrice)+',TP '+str(price)
                            elif bonus_type=='Percentage':
                                newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
                                short_note='Approved '+str(fixed_percent_rate)+'% of TP '+str(price)
                            #-----------
                            bonus_qty=0                        
                            totalAmountTP+=round(item_qty_value*newPrice,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)                
                            
                            #------------ set batch id after checking stock
                            requestBaseQty=item_qty_value
                            
                            stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                            for stockRow in stockRows:
                                batch_id=stockRow.batch_id
                                quantity=stockRow.quantity
                                block_qty=stockRow.block_qty
                                availableQty=quantity-block_qty
                                
                                if requestBaseQty<=availableQty:
                                    newBlockQty=block_qty+requestBaseQty
                                    newBaseQty=requestBaseQty
                                    requestBaseQty=0
                                    
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)                        
                                    stockRow.update_record(block_qty=newBlockQty)                        
                                    break
                                else:
                                    newBlockQty=block_qty+availableQty
                                    newBaseQty=availableQty
                                    requestBaseQty=requestBaseQty-availableQty
                                    
                                    #--------------
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                    detailList.append(detailDict)
                                    stockRow.update_record(block_qty=newBlockQty)
                                    
                            #--------------
                            if requestBaseQty>0:
                                batch_id=''
                                emptyBatchFlag=1
                                detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                                detailList.append(detailDict)
                                
                            #---------------------------------------                            
                            promoFlag=1                        
                            ordRec.update_record(ar_flag=1)
                            break
            
            #-------- step-5: Declared Item           
            ordRecords5=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)&(db.sm_tp_rules_temp_process_manual.fr_flag==0)&(db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.status=='ACTIVE')&(db.sm_tp_rules_temp_process_manual.item_id==db.sm_promo_declared_item.product_id)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRec in ordRecords5:             
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                
                short_note='Declared Item'
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #-----------
                bonus_qty=0
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)
                
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1 
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
                    
                #---------------------------------------                
                promoFlag=1                        
                ordRec.update_record(di_flag=1)
                
            #-------- step-6: Regular Discount            
            ordRec6Qset=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)&(db.sm_tp_rules_temp_process_manual.fr_flag==0)&(db.sm_tp_rules_temp_process_manual.di_flag==0))
            ordRec6Rows=ordRec6Qset.select(db.sm_tp_rules_temp_process_manual.quantity,db.sm_tp_rules_temp_process_manual.price,db.sm_tp_rules_temp_process_manual.item_vat)
            if ordRec6Rows:
                #totalAmt=0                
            #     for ordRec6Row in ordRec6Rows:
            #         quantity=ordRec6Row.quantity
            #         price=ordRec6Row.price
            #         #item_vat=ordRec6Row.item_vat
            #         totalAmt+=quantity*price
            # # discount calculation
            # discountRows=db((db.sm_promo_regular_discount.cid==c_id)&(db.sm_promo_regular_discount.from_date<=orderDate)&(db.sm_promo_regular_discount.to_date>=orderDate) & (db.sm_promo_regular_discount.status=='ACTIVE')&(db.sm_promo_regular_discount.min_amount<=totalAmt)).select(db.sm_promo_regular_discount.discount_precent,orderby=~db.sm_promo_regular_discount.min_amount,limitby=(0,1))
            # if discountRows:
            #     discount_precent=discountRows[0].discount_precent
            #
            #     discount=round((totalAmt*discount_precent)/100,2)
                
                ordRecords6=ordRec6Qset.select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
                for ordRec in ordRecords6:             
                    item_id=str(ordRec.item_id).strip().upper()
                    item_name=ordRec.item_name
                    category_id=ordRec.category_id
                    actual_tp=ordRec.actual_tp
                    actual_vat=ordRec.actual_vat
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.price)
                    item_vat=float(ordRec.item_vat)
                    item_unit=ordRec.item_unit
                    item_carton=ordRec.item_carton
                        
                    short_note='Regular Discount'
                    promotion_type=''
                    bonus_applied_on_qty=0
                    circular_no=''
                    
                    #-----------
                    bonus_qty=0
                    totalAmountTP+=round(item_qty_value*price,6)
                    totalAmountVat+=round(item_qty_value*item_vat,6)
                    
                    #------------ set batch id after checking stock
                    requestBaseQty=item_qty_value
                    
                    stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                    for stockRow in stockRows:
                        batch_id=stockRow.batch_id
                        quantity=stockRow.quantity
                        block_qty=stockRow.block_qty
                        availableQty=quantity-block_qty
                        
                        if requestBaseQty<=availableQty:
                            newBlockQty=block_qty+requestBaseQty
                            newBaseQty=requestBaseQty
                            requestBaseQty=0
                            
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)                        
                            stockRow.update_record(block_qty=newBlockQty)                        
                            break
                        else:
                            newBlockQty=block_qty+availableQty
                            newBaseQty=availableQty
                            requestBaseQty=requestBaseQty-availableQty
                            
                            #--------------
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                            detailList.append(detailDict)
                            stockRow.update_record(block_qty=newBlockQty)
                            
                    #--------------
                    if requestBaseQty>0:
                        batch_id=''
                        emptyBatchFlag=1        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        
                    #---------------------------------------                    
                    promoFlag=1
                    ordRec.update_record(rd_flag=1)

            # --- 7 discount for all
            ordRec7Qset = db((db.sm_tp_rules_temp_process_manual.cid == c_id) & (
                        db.sm_tp_rules_temp_process_manual.depot_id == depot_id) & (
                                         db.sm_tp_rules_temp_process_manual.sl == invoice_sl))
            ordRec7Rows = ordRec7Qset.select(db.sm_tp_rules_temp_process_manual.quantity,
                                             db.sm_tp_rules_temp_process_manual.price,
                                             db.sm_tp_rules_temp_process_manual.item_vat)
            if ordRec7Rows:
                totalAmt=0
                for ordRec7Row in ordRec7Rows:
                    quantity = ordRec7Row.quantity
                    price = ordRec7Row.price
                    # item_vat=ordRec6Row.item_vat
                    totalAmt += quantity * price
            # discount calculation
            discountRows = db(
                (db.sm_promo_regular_discount.cid == c_id) & (db.sm_promo_regular_discount.from_date <= orderDate) & (
                            db.sm_promo_regular_discount.to_date >= orderDate) & (
                            db.sm_promo_regular_discount.status == 'ACTIVE') & (
                            db.sm_promo_regular_discount.min_amount <= totalAmt)).select(
                db.sm_promo_regular_discount.discount_precent, orderby=~db.sm_promo_regular_discount.min_amount,
                limitby=(0, 1))
            if discountRows:
                discount_precent = discountRows[0].discount_precent

                discount = round((totalAmt * discount_precent) / 100, 2)


            #------------ step-Last
            ordRecordsLast=db((db.sm_tp_rules_temp_process_manual.cid==c_id) & (db.sm_tp_rules_temp_process_manual.depot_id==depot_id)&(db.sm_tp_rules_temp_process_manual.sl==invoice_sl)&(db.sm_tp_rules_temp_process_manual.prio_flag==0)&(db.sm_tp_rules_temp_process_manual.ar_flag==0)&(db.sm_tp_rules_temp_process_manual.pb_flag==0)&(db.sm_tp_rules_temp_process_manual.sr_flag==0)&(db.sm_tp_rules_temp_process_manual.fr_flag==0)&(db.sm_tp_rules_temp_process_manual.di_flag==0)&(db.sm_tp_rules_temp_process_manual.rd_flag==0)).select(db.sm_tp_rules_temp_process_manual.ALL,orderby=db.sm_tp_rules_temp_process_manual.item_name)
            for ordRec in ordRecordsLast:
                item_id=str(ordRec.item_id).strip().upper()
                item_name=ordRec.item_name
                category_id=ordRec.category_id
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.price)   
                item_vat=float(ordRec.item_vat)
                item_unit=ordRec.item_unit
                item_carton=ordRec.item_carton
                            
                bonus_qty=0                
                totalAmountTP+=round(item_qty_value*price,6)
                totalAmountVat+=round(item_qty_value*item_vat,6)            
                short_note='-'
                
                promotion_type=''
                bonus_applied_on_qty=0
                circular_no=''
                
                #detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'category_id':category_id,'quantity':item_qty_value,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'note':req_note,'short_note':short_note,'status':'Submitted'}
                #detailList.append(detailDict)
                
                #------------ set batch id after checking stock
                requestBaseQty=item_qty_value
                
                stockRows=db((db.sm_depot_stock_balance.cid==c_id)& (db.sm_depot_stock_balance.depot_id==depot_id) & (db.sm_depot_stock_balance.store_id==store_id) & (db.sm_depot_stock_balance.item_id==item_id) & (db.sm_depot_stock_balance.quantity>db.sm_depot_stock_balance.block_qty)).select(db.sm_depot_stock_balance.id,db.sm_depot_stock_balance.batch_id,db.sm_depot_stock_balance.quantity,db.sm_depot_stock_balance.block_qty,orderby=db.sm_depot_stock_balance.expiary_date)
                for stockRow in stockRows:
                    batch_id=stockRow.batch_id
                    quantity=stockRow.quantity
                    block_qty=stockRow.block_qty
                    availableQty=quantity-block_qty
                    
                    if requestBaseQty<=availableQty:
                        newBlockQty=block_qty+requestBaseQty
                        newBaseQty=requestBaseQty
                        requestBaseQty=0
                        
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)                        
                        stockRow.update_record(block_qty=newBlockQty)                        
                        break
                    else:
                        newBlockQty=block_qty+availableQty
                        newBaseQty=availableQty
                        requestBaseQty=requestBaseQty-availableQty
                        
                        #--------------
                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                        detailList.append(detailDict)
                        stockRow.update_record(block_qty=newBlockQty)
                        
                #--------------
                if requestBaseQty>0:
                    batch_id=''
                    emptyBatchFlag=1
                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'store_id':store_id,'store_name':store_name,'order_sl':sl,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'market_id':market_id,'market_name':market_name,'area_id':area_id,'area_name':area_name,'invoice_media':order_media,'device_user_agent':'','ip_ref':'','ym_date':ym_date,'payment_mode':payment_mode,'item_id':item_id,'item_name':item_name,'batch_id':batch_id,'category_id':category_id,'actual_tp':actual_tp,'actual_vat':actual_vat,'quantity':requestBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat,'sp_discount_item':0,'item_unit':item_unit,'item_carton':item_carton,'promotion_type':promotion_type,'bonus_applied_on_qty':bonus_applied_on_qty,'circular_no':circular_no,'note':req_note,'short_note':short_note,'status':'Submitted'}
                    detailList.append(detailDict)
                    
                #---------------------------------------
                
    discount=round(float(discount),2)
    totalAmount=(round(totalAmountTP,2)+round(totalAmountVat,2)-discount)
    
    sp_discount=round(float(sp_discount),2)
    
    retMsg=''
    #=============== Insert invoice head and details
    if (len(headList)> 0 and len(detailList) > 0):
        
        #----------- check credit policy
        limitOverFlag=0
        acknowledge_flag=0
        if payment_mode!='CASH':
            acknowledge_flag=1
            creditPolicyRow=db((db.sm_cp_approved.cid==c_id)&(db.sm_cp_approved.client_id==client_id)&(db.sm_cp_approved.status=='ACTIVE')).select(db.sm_cp_approved.credit_amount,limitby=(0,1))
            if not creditPolicyRow:
                limitOverFlag=1
            else:
                credit_amount=creditPolicyRow[0].credit_amount
                
                tx_closing_balance=0
                ledgerRow=db((db.sm_transaction.cid==c_id)&(db.sm_transaction.tx_account=='CLT-'+str(client_id))&(db.sm_transaction.opposite_account=='DPT-'+str(depot_id))).select(db.sm_transaction.tx_closing_balance,orderby=~db.sm_transaction.tx_date,limitby=(0,1))
                if ledgerRow:
                    tx_closing_balance=ledgerRow[0].tx_closing_balance            
                clientTotal=tx_closing_balance+totalAmount
                
                if clientTotal>credit_amount:
                    limitOverFlag=1
                    
        #----------- end check credit policy
        
        level0_id=''
        level0_name=''
        level1_id=''
        level1_name=''
        level2_id=''
        level2_name=''
        level3_id=''
        level3_name=''
        orderHRow=db((db.sm_invoice_head.cid==c_id) & (db.sm_invoice_head.depot_id==depot_id) &(db.sm_invoice_head.sl==invoice_sl)).select(db.sm_invoice_head.level0_id,db.sm_invoice_head.level0_name,db.sm_invoice_head.level1_id,db.sm_invoice_head.level1_name,db.sm_invoice_head.level2_id,db.sm_invoice_head.level2_name,db.sm_invoice_head.level3_id,db.sm_invoice_head.level3_name,limitby=(0,1))
        if orderHRow:
            level0_id=orderHRow[0].level0_id
            level0_name=orderHRow[0].level0_name
            level1_id=orderHRow[0].level1_id
            level1_name=orderHRow[0].level1_name
            level2_id=orderHRow[0].level2_id
            level2_name=orderHRow[0].level2_name
            level3_id=orderHRow[0].level3_id
            level3_name=orderHRow[0].level3_name
            
        #---------- dicount amount assigned
        for i in range(len(headList)):
            headDictData=headList[i]
            headDictData['discount']=discount
            headDictData['client_limit_over']=limitOverFlag
            headDictData['empty_batch_flag']=emptyBatchFlag
            headDictData['acknowledge_flag']=acknowledge_flag
            headDictData['level0_id']=level0_id
            headDictData['level0_name']=level0_name
            headDictData['level1_id']=level1_id
            headDictData['level1_name']=level1_name
            headDictData['level2_id']=level2_id
            headDictData['level2_name']=level2_name
            headDictData['level3_id']=level3_id
            headDictData['level3_name']=level3_name
            headDictData['discount_precent']=discount_precent
            headDictData['sp_discount']=sp_discount
            
        for j in range(len(detailList)):
            detailDictData=detailList[j]
            detailDictData['discount']=discount
            detailDictData['level0_id']=level0_id
            detailDictData['level0_name']=level0_name
            detailDictData['level1_id']=level1_id
            detailDictData['level1_name']=level1_name
            detailDictData['level2_id']=level2_id
            detailDictData['level2_name']=level2_name
            detailDictData['level3_id']=level3_id
            detailDictData['level3_name']=level3_name
            
        #-------------
        #Update status of head and detail       
        
        db((db.sm_invoice_head.cid==c_id) & (db.sm_invoice_head.depot_id==depot_id) &(db.sm_invoice_head.sl==invoice_sl)).delete()
        db((db.sm_invoice.cid==c_id) & (db.sm_invoice.depot_id==depot_id) &(db.sm_invoice.sl==invoice_sl)).delete()
        
        rows=db.sm_invoice.bulk_insert(detailList)
        rows=db.sm_invoice_head.bulk_insert(headList)                        
        
        retMsg='Processed Successfully '
        db.commit()
        
    #-------------- end order
    
    return retMsg



#***** new return with promotion
# change:- parameter, insert into temp, sm_tp_rules_temp_process~>sm_tp_rules_temp_return, order_sl~>return_sl

def get_rules_return(cid,depot_id,return_sl,invoice_sl,clientId,orderDate):
    c_id=cid
    depot_id=depot_id
    sl=return_sl
    client_id=clientId
    orderDate=orderDate
    
    #========================-get settings flag
    invoiceRulesFlag=False
    
    compSttRows=db((db.sm_settings.cid==c_id)&(db.sm_settings.s_key=='INVOICE_RULES')&(db.sm_settings.s_value=='YES')).select(db.sm_settings.cid,limitby=(0,1))
    if compSttRows:
        invoiceRulesFlag=True
        
    #================ if invoice rules are to apply (Note: ANY or Sepcific item, at a time two rules not applicable)
    productBonusPriorityRows=''
    approvedItemRows=''    
    productBonusRows=''
    specialRateRows=''
    flatRateRows=''
    promo_ref=0 #0=No,1=Yes
    if invoiceRulesFlag==True:        
        orderHeadRow=db((db.sm_invoice_head.cid==c_id) & (db.sm_invoice_head.depot_id==depot_id) & (db.sm_invoice_head.sl==invoice_sl)).select(db.sm_invoice_head.promo_ref,limitby=(0,1))
        if orderHeadRow:
            promo_ref=orderHeadRow[0].promo_ref
            if promo_ref!=0:
                promo_ref=1
                
        #approvedItemRows=db((db.sm_promo_approved_rate.cid==c_id)&(db.sm_promo_approved_rate.client_id==client_id)&(db.sm_promo_approved_rate.from_date<=orderDate)&(db.sm_promo_approved_rate.to_date>=orderDate)&(db.sm_promo_approved_rate.status=='ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date|db.sm_promo_approved_rate.product_id)
        productBonusRows=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,db.sm_promo_product_bonus.until_stock_last,db.sm_promo_product_bonus.allowed_credit_inv,db.sm_promo_product_bonus.regular_discount_apply,orderby=~db.sm_promo_product_bonus.min_qty)       #&(db.sm_promo_product_bonus.id!=promo_ref)
        specialRateRows=db((db.sm_promo_special_rate.cid==c_id)&(db.sm_promo_special_rate.from_date<=orderDate)&(db.sm_promo_special_rate.to_date>=orderDate)&(db.sm_promo_special_rate.status=='ACTIVE')).select(db.sm_promo_special_rate.product_id,db.sm_promo_special_rate.min_qty,db.sm_promo_special_rate.special_rate_tp,db.sm_promo_special_rate.special_rate_vat,db.sm_promo_special_rate.allowed_credit_inv,db.sm_promo_special_rate.regular_discount_apply,orderby=~db.sm_promo_special_rate.from_date)
        flatRateRows=db((db.sm_promo_flat_rate.cid==c_id)&(db.sm_promo_flat_rate.from_date<=orderDate)&(db.sm_promo_flat_rate.to_date>=orderDate)&(db.sm_promo_flat_rate.status=='ACTIVE')).select(db.sm_promo_flat_rate.campaign_ref,db.sm_promo_flat_rate.product_id,db.sm_promo_flat_rate.min_qty,db.sm_promo_flat_rate.flat_rate,db.sm_promo_flat_rate.allowed_credit_inv,db.sm_promo_flat_rate.regular_discount_apply,db.sm_promo_flat_rate.allow_bundle,orderby=~db.sm_promo_flat_rate.from_date)

        # common approved rate
        approvedItemRows = db((db.sm_promo_approved_rate.cid == c_id) & (db.sm_promo_approved_rate.from_date <= orderDate) & (db.sm_promo_approved_rate.to_date >= orderDate) & (db.sm_promo_approved_rate.status == 'ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date | db.sm_promo_approved_rate.product_id)

    #----------- get delivery max sl from depot
     
    maxSl=return_sl
     
    records=''
    #---------------   order detail records
                                   
    detailDict={}
    detailList=[]                            
         
    totalAmountTP=0
    totalAmountVat=0
    discount=0    
    discount_precent=0
    #order details loop      
    orderRecords=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)).select(db.sm_tp_rules_temp_return.ALL,limitby=(0,1))
    if orderRecords:        
        return_sl=orderRecords[0].return_sl        
        invoice_sl=orderRecords[0].invoice_sl
        payment_mode=orderRecords[0].payment_mode
        
        emptyBatchFlag=0
        if invoiceRulesFlag==False:
            #=========================== Rules not apply
            retMsg='Rules not applicable'
            return retMsg
        else:
            #===================== Rules apply 
            promoFlag=0
            totalAmt=0
            
            #-------- step-0: Priority (Product Bonus)
            if promo_ref==0:
                #-------- step-1: Approved rate            
                ordRecords1=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
                for ordRec in ordRecords1:             
                    item_id=str(ordRec.item_id).strip().upper()                    
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.ret_price)   
                    item_vat=float(ordRec.ret_item_vat)                    
                    ret_rowid=ordRec.ret_rowid
                    
                    for appItemRow in approvedItemRows:
                        product_id=str(appItemRow.product_id).strip().upper()
                        bonus_type=appItemRow.bonus_type
                        fixed_percent_rate=appItemRow.fixed_percent_rate
                        
                        if product_id==item_id:
                            newPrice=price
                            promotion_type='APPROVED'
                            bonus_applied_on_qty=0
                            circular_no=''
                            
#                             if bonus_type=='Fixed':
#                                 newPrice=fixed_percent_rate                                
#                             elif bonus_type=='Percentage':
#                                 newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
                                
                            #-----------
                            bonus_qty=0
                            totalAmountTP+=round(item_qty_value*newPrice,2)
                            totalAmountVat+=round(item_qty_value*item_vat,2)                
                            
                            newBaseQty=item_qty_value
                            #------------ set batch id after checking stock                            
                            detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat}
                            detailList.append(detailDict)                        
                            
                            #---------------------------------------                            
                            promoFlag=1                        
                            ordRec.update_record(ar_flag=1)
                            break
            
            #-------- step-2: Product Bonus
            for prodBonusRow in productBonusRows:      
                rowid=prodBonusRow.id
                circular_number=prodBonusRow.circular_number
                min_qty=prodBonusRow.min_qty                
                allowed_credit_inv=str(prodBonusRow.allowed_credit_inv).strip().upper()      #for bonus
                regular_discount_apply=str(prodBonusRow.regular_discount_apply).strip().upper()  #for product full qty
                
                allowBonus='YES'
                if payment_mode!='CASH':
                    if allowed_credit_inv=='NO':
                        allowBonus='NO'
                        
                if allowBonus=='NO':
                    continue
                    
                pbQset=db((db.sm_promo_product_bonus_products.cid==c_id)&(db.sm_promo_product_bonus_products.refrowid==rowid)&(db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_promo_product_bonus_products.product_id==db.sm_tp_rules_temp_return.item_id))
                totalQtyRows=pbQset.select(db.sm_tp_rules_temp_return.quantity.sum(),groupby=db.sm_tp_rules_temp_return.cid)
                
                if totalQtyRows:
                    qtyCount=totalQtyRows[0][db.sm_tp_rules_temp_return.quantity.sum()]
                    
                    if qtyCount>=min_qty:                        
                        fullCount=int(qtyCount/min_qty)
                        
                        #===================================== for bonus calculate
                        circularStr=circular_number
                        
                        nextQtyCount=qtyCount-min_qty*fullCount
                        
                        regularQty=0       #extra Qty
                        discountRate=0
                        
                        itemFullQty=min_qty*fullCount
                        
                        bonusDictList=[]
                        bonusDictList.append({'rowid':rowid,'fullCount':fullCount,'circularNo':circular_number})
                        
                        if nextQtyCount>0:
                            prodPromList=[]
                            totalItemRows=pbQset.select(db.sm_tp_rules_temp_return.item_id,groupby=db.sm_tp_rules_temp_return.item_id)
                            for totItemRow in totalItemRows:                            
                                prodPromList.append(totItemRow.item_id)
                                
                            productBonusRows2=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')&(db.sm_promo_product_bonus.id!=rowid)&(db.sm_promo_product_bonus.id==db.sm_promo_product_bonus_products.refrowid)&(db.sm_promo_product_bonus_products.product_id.belongs(prodPromList))).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,orderby=~db.sm_promo_product_bonus.min_qty,groupby=db.sm_promo_product_bonus.id)
                            if productBonusRows2:                            
                                for productBonusRow2 in productBonusRows2:      
                                    rowid2=productBonusRow2.id
                                    circular_number2=productBonusRow2.circular_number
                                    min_qty2=productBonusRow2.min_qty
                                    
                                    if nextQtyCount>=min_qty2:
                                        fullCount2=int(nextQtyCount/min_qty2)
                                        
                                        circularStr+=','+str(circular_number2)
                                        bonusDictList.append({'rowid':rowid2,'fullCount':fullCount2,'circularNo':circular_number2})
                                        
                                        nextQtyCount=nextQtyCount-min_qty2*fullCount2
                                        itemFullQty+=min_qty2*fullCount2
                                              
                                    else:                                        
                                        break
                                        
                                if nextQtyCount>0:
                                    regularQty=nextQtyCount
                                    #discount apply
                            else:
                                regularQty=nextQtyCount
                                #discount apply
                        #----------
                        #------ insert and update flag
                        regularQtyDisFlag='YES'           
                        bonusOnQty=itemFullQty
                        regularQtyAmt=0
                                     
                        ordRecords2=pbQset.select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
                        for ordRec in ordRecords2:
                            item_id=str(ordRec.item_id).strip().upper()                            
                            item_qty_value=int(ordRec.quantity)
                            actual_tp=ordRec.actual_tp
                            actual_vat=ordRec.actual_vat                            
                            price=float(ordRec.ret_price)   
                            item_vat=float(ordRec.ret_item_vat)
                            ret_rowid=ordRec.ret_rowid
                            
                            #------------------
                            discount_rate=price
                            
                            specialNote=''                        
                            for spRateRow in specialRateRows:
                                product_id=str(spRateRow.product_id).strip().upper()
                                minQty=spRateRow.min_qty
                                special_rate_tp=spRateRow.special_rate_tp
                                special_rate_vat=spRateRow.special_rate_vat                                
                                allowed_credit_inv=str(spRateRow.allowed_credit_inv).strip().upper()                                
                                if product_id==item_id:
                                    allowSpecialRate='YES'
                                    if payment_mode!='CASH':
                                        if allowed_credit_inv=='NO':
                                            allowSpecialRate='NO'                        
                                            
                                    #check special rate applicable
                                    if allowSpecialRate=='NO':
                                        #price=special_rate_tp
                                        #item_vat=special_rate_vat                     
                                        #specialNote=' with Special Rate (Premium TP) and vat applied'                                    
                                        #actual_tp=special_rate_tp
                                        #actual_vat=special_rate_vat
                                        regular_discount_apply='YES'
                                        break
                                    else:
                                        if item_qty_value<minQty:
                                            #price=special_rate_tp
                                            #item_vat=special_rate_vat                     
                                            #specialNote=' with Special Rate (Premium TP) and vat applied'                                    
                                            #actual_tp=special_rate_tp
                                            #actual_vat=special_rate_vat
                                            regular_discount_apply='YES'
                                            break
                                        else:
                                            regular_discount_apply='NO'
                                            regularQtyDisFlag='NO'                                   
                                            break
                            #-----------
                            bonus_qty=0
                            totalAmountTP+=round(item_qty_value*price,6)
                            totalAmountVat+=round(item_qty_value*item_vat,6)
                            
                            regQty=0
                            promotion_type='BONUS'                            
                            if bonusOnQty>item_qty_value:
                                bonus_applied_on_qty=item_qty_value
                                bonusOnQty=bonusOnQty-item_qty_value                                
                            else:
                                bonus_applied_on_qty=bonusOnQty
                                
                                regQty=int(item_qty_value-bonusOnQty)
                                bonusOnQty=0
                            
                            circular_no=str(circularStr)
                            
                            #----------- new code
                            declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                            if not declaredItemRow:
                                discountRate=discount_rate
                                #regular rate, applied discount
                                
                                if regular_discount_apply=='YES': #apply for all qty
                                    totalAmt+=round(item_qty_value*price,2)
                                    #short_note+=' and regular discount'
                                else:
                                    #if regularQty>0 and :
                                        #short_note+=' and regular discount on '+str(regularQty)+' Quantity'
                                        #pass
                                    if regularQty>0 and regQty>0:
                                        if regularQtyDisFlag=='YES':                                            
                                            regularQtyAmt+=regQty*price
                                            
                            #------------ set batch id after checking stock
                            newBaseQty=item_qty_value                            
                            detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
                            detailList.append(detailDict)
                            
                            #---------------------------------------                            
                            promoFlag=1                            
                            ordRec.update_record(pb_flag=1)
                            
                        if regular_discount_apply!='YES': #apply for all qty
                            #new code
                            #product bonus rest qty discount apply
                            if regularQtyDisFlag=='YES':
                                #totalAmt+=round(regularQty*discountRate,2)
                                totalAmt+=round(regularQtyAmt,2)
                                
                        #if bonusStockFlag=='YES':
                        #--------- bonus item insert                        
                        for k in range(len(bonusDictList)):
                            bonusDictData=bonusDictList[k]
                            
                            bRowid=bonusDictData['rowid']
                            bfullCount=bonusDictData['fullCount']
                            bcircularNo=bonusDictData['circularNo']
                            #end new code next use bRowid
                            
                            #--------- bonus item add
                            bonusRows=db((db.sm_promo_product_bonus_bonuses.cid==c_id)&(db.sm_promo_product_bonus_bonuses.refrowid==bRowid)&(db.sm_item.cid==c_id)&(db.sm_item.item_id==db.sm_promo_product_bonus_bonuses.bonus_product_id)).select(db.sm_promo_product_bonus_bonuses.bonus_product_id,db.sm_item.name,db.sm_item.category_id,db.sm_item.category_id_sp,db.sm_item.unit_type,db.sm_item.item_carton,db.sm_promo_product_bonus_bonuses.bonus_qty)
                            for bonusRow in bonusRows:
                                bonus_product_id=bonusRow.sm_promo_product_bonus_bonuses.bonus_product_id                                
                                bonus_item_qty=bonusRow.sm_promo_product_bonus_bonuses.bonus_qty
                                actual_tp=0
                                actual_vat=0
                                #----
                                item_id=bonus_product_id                                
                                item_qty_value=0
                                bonus_qty=bonus_item_qty*bfullCount
                                newPrice=0
                                item_vat=0                                
                                ret_rowid=0                                 
                                
                                #------------ set batch id after checking stock
                                newBaseQty=bonus_qty
                                detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':item_qty_value,'bonus_qty':newBaseQty,'price':newPrice,'item_vat':item_vat}
                                detailList.append(detailDict)
                                
                                #---------------------------------------                                
                                promoFlag=1
                    
                    #------------
            
            #-------- step-3: Special rate
            ordRecords3=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
            for ordRec in ordRecords3:             
                item_id=str(ordRec.item_id).strip().upper()                
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.ret_price)
                item_vat=float(ordRec.ret_item_vat)                
                ret_rowid=ordRec.ret_rowid
                
                for spRateRow in specialRateRows:
                    product_id=str(spRateRow.product_id).strip().upper()
                    min_qty=spRateRow.min_qty
                    special_rate_tp=spRateRow.special_rate_tp
                    special_rate_vat=spRateRow.special_rate_vat
                    
                    allowed_credit_inv=str(spRateRow.allowed_credit_inv).strip().upper()
                    regular_discount_apply=str(spRateRow.regular_discount_apply).strip().upper()
                    
                    if product_id==item_id:
                        allowSpecialRate='YES'
                        if payment_mode!='CASH':
                            if allowed_credit_inv=='NO':
                                allowSpecialRate='NO'                        
                        
                        #check special rate applicable                        
                        if allowSpecialRate=='NO':
                            #newPrice=special_rate_tp
                            regular_discount_apply='YES'
                            #short_note='Special Rate (Premium TP) and vat applied'
                            #actual_tp=special_rate_tp
                            #actual_vat=special_rate_vat                            
                        else:
                            if item_qty_value<min_qty:
                                #newPrice=special_rate_tp
                                regular_discount_apply='YES'
                                #short_note='Special Rate (Premium TP) and vat applied'                            
                                #actual_tp=special_rate_tp
                                #actual_vat=special_rate_vat                            
                            else:
                                #newPrice=price
                                regular_discount_apply='NO'
                                #short_note='Special Rate and vat applied'
                        
                        newPrice=price
                        newVat=item_vat 
                        
                        #-----------
                        bonus_qty=0                        
                        totalAmountTP+=round(item_qty_value*newPrice,6)
                        totalAmountVat+=round(item_qty_value*newVat,6)
                        
                        if regular_discount_apply=='YES': #apply for all qty
                            #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                            declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                            if not declaredItemRow:                                                                       
                                totalAmt+=round(item_qty_value*newPrice,2)                                    
                                #short_note+=' and regular discount'
                                
                        #------------ set batch id after checking stock                        
                        newBaseQty=item_qty_value
                        detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat}
                        detailList.append(detailDict)
                        
                        #---------------------------------------                        
                        promoFlag=1                        
                        ordRec.update_record(sr_flag=1)
                        break
                        
            #-------- step-4: Flat rate            
            ordRecords4=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
            for ordRec in ordRecords4:             
                item_id=str(ordRec.item_id).strip().upper()   
                actual_tp=ordRec.actual_tp
                actual_vat=ordRec.actual_vat             
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.ret_price)
                item_vat=float(ordRec.ret_item_vat)
                ret_rowid=ordRec.ret_rowid
                
                for flatRateRow in flatRateRows:
                    campaign_ref=str(flatRateRow.campaign_ref).strip()
                    product_id=str(flatRateRow.product_id).strip().upper()
                    min_qty=flatRateRow.min_qty
                    flat_rate=flatRateRow.flat_rate
                    
                    allowed_credit_inv=str(flatRateRow.allowed_credit_inv).strip().upper()
                    regular_discount_apply=str(flatRateRow.regular_discount_apply).strip().upper()
                    allow_bundle=str(flatRateRow.allow_bundle).strip().upper()  #for different processing rules
                    
                    if product_id==item_id and item_qty_value>=min_qty:
                        allowFlatRate='YES'
                        if payment_mode!='CASH':
                            if allowed_credit_inv=='NO':
                                allowFlatRate='NO'
                        
                        #check flat rate applicable
                        if allowFlatRate=='NO':
                            break
                            
                        #------------------------------Allow per bundle calculated and extra will be regular rate
                        if allow_bundle=='YES':                        
                            regularQty=(item_qty_value%min_qty)
                            fullQty=item_qty_value-regularQty
                            
                            #newPrice=flat_rate                         
                            #short_note='Flat Rate applied'
                            promotion_type='FLAT'
                            bonus_applied_on_qty=0
                            circular_no=campaign_ref
                            
                            newPrice=price 
                            
                            #-----------
                            bonus_qty=0
                            
                            totalAmountTP+=round(fullQty*newPrice,6)
                            totalAmountVat+=round(fullQty*item_vat,6)
                            
                            if regular_discount_apply=='YES': #apply for all qty
                                #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:                                                                       
                                    totalAmt+=round(fullQty*newPrice,2)                                    
                                    #short_note+=' and regular discount'
                                    
                            #------------ set batch id after checking stock                            
                            newBaseQty=fullQty                            
                            detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat}
                            detailList.append(detailDict)
                            
                            #---------------------------------------                        
                            if regularQty>0:                                                                        
                                #short_note='Flat Rate balance regular rate, declared item'
                                promotion_type=''
                                bonus_applied_on_qty=0
                                circular_no=''
                                
                                #-----------
                                bonus_qty=0                            
                                totalAmountTP+=round(regularQty*price,6)
                                totalAmountVat+=round(regularQty*item_vat,6)
                                
                                #-----------
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:
                                    totalAmt+=round(regularQty*price,2)
                                    #short_note='Flat Rate balance regular rate and applied regular discount'
                                    
                                #------------ set batch id after checking stock                                
                                newBaseQty=regularQty                                
                                detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
                                detailList.append(detailDict) 
                                
                        #---------------------------------------    All quantity regular rate if minimum rate matching                        
                        else:                            
                            fullQty=item_qty_value
                            
                            #newPrice=flat_rate                                               
                            #short_note='Flat Rate applied'
                            
                            newPrice=price
                            
                            promotion_type='FLAT'
                            bonus_applied_on_qty=0
                            circular_no=campaign_ref
                            
                            #-----------
                            bonus_qty=0
                            
                            totalAmountTP+=round(fullQty*newPrice,6)
                            totalAmountVat+=round(fullQty*item_vat,6)
                            
                            if regular_discount_apply=='YES': #apply for all qty
                                #----------- new code (if bonus product many than last item rate is used for regular qty,all discount apply flag=NO)
                                declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
                                if not declaredItemRow:
                                    discountRate=newPrice
                                    #regular rate, applied discount                                    
                                    totalAmt+=round(fullQty*discountRate,2)
                                    #short_note+=' and regular discount'
                            
                            #------------ set batch id after checking stock                            
                            newBaseQty=fullQty                                
                            detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat}
                            detailList.append(detailDict) 
                            
                            #---------------------------------------
                        
                        promoFlag=1                        
                        ordRec.update_record(fr_flag=1)
                        break
            #-------- promo ref=1 then aproved rate later
            if promo_ref==1:
                #-------- step-1: Approved rate            
                ordRecords1=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)&(db.sm_tp_rules_temp_return.fr_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
                for ordRec in ordRecords1:             
                    item_id=str(ordRec.item_id).strip().upper()                    
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.ret_price)   
                    item_vat=float(ordRec.ret_item_vat)                    
                    ret_rowid=ordRec.ret_rowid
                    
                    for appItemRow in approvedItemRows:
                        product_id=str(appItemRow.product_id).strip().upper()
                        bonus_type=appItemRow.bonus_type
                        fixed_percent_rate=appItemRow.fixed_percent_rate
                        
                        if product_id==item_id:
                            newPrice=price
                            promotion_type='APPROVED'
                            bonus_applied_on_qty=0
                            circular_no=''
                            
#                             if bonus_type=='Fixed':
#                                 newPrice=fixed_percent_rate                                
#                             elif bonus_type=='Percentage':
#                                 newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
                                
                            #-----------
                            bonus_qty=0
                            totalAmountTP+=round(item_qty_value*newPrice,2)
                            totalAmountVat+=round(item_qty_value*item_vat,2)                
                            
                            newBaseQty=item_qty_value
                            #------------ set batch id after checking stock                            
                            detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat}
                            detailList.append(detailDict)                        
                            
                            #---------------------------------------                            
                            promoFlag=1                        
                            ordRec.update_record(ar_flag=1)
                            break
            
            #-------- step-5: Declared Item           
            ordRecords5=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)&(db.sm_tp_rules_temp_return.fr_flag==0)&(db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.status=='ACTIVE')&(db.sm_tp_rules_temp_return.item_id==db.sm_promo_declared_item.product_id)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
            for ordRec in ordRecords5:             
                item_id=str(ordRec.item_id).strip().upper()                
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.ret_price)
                item_vat=float(ordRec.ret_item_vat)                
                ret_rowid=ordRec.ret_rowid
                
                #-----------
                bonus_qty=0
                totalAmountTP+=round(item_qty_value*price,2)
                totalAmountVat+=round(item_qty_value*item_vat,2)
                
                #------------ set batch id after checking stock
                newBaseQty=item_qty_value
                
                detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
                detailList.append(detailDict)
                 
                #---------------------------------------                
                promoFlag=1                        
                ordRec.update_record(di_flag=1)
            
            #-------- step-6: Regular Discount            
            ordRec6Qset=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)&(db.sm_tp_rules_temp_return.fr_flag==0)&(db.sm_tp_rules_temp_return.di_flag==0))
            ordRec6Rows=ordRec6Qset.select(db.sm_tp_rules_temp_return.quantity,db.sm_tp_rules_temp_return.ret_price,db.sm_tp_rules_temp_return.ret_item_vat)
            if ordRec6Rows:
                #totalAmt=0                
                for ordRec6Row in ordRec6Rows:             
                    quantity=ordRec6Row.quantity
                    price=ordRec6Row.ret_price
                    #item_vat=ordRec6Row.item_vat                    
                    totalAmt+=quantity*price
            # discount calculation
            discountRows=db((db.sm_promo_regular_discount.cid==c_id)&(db.sm_promo_regular_discount.from_date<=orderDate)&(db.sm_promo_regular_discount.to_date>=orderDate) & (db.sm_promo_regular_discount.status=='ACTIVE')&(db.sm_promo_regular_discount.min_amount<=totalAmt)).select(db.sm_promo_regular_discount.discount_precent,orderby=~db.sm_promo_regular_discount.min_amount,limitby=(0,1))
            if discountRows:
                discount_precent=discountRows[0].discount_precent
                
                discount=round((totalAmt*discount_precent)/100,2)
                
                ordRecords6=ordRec6Qset.select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
                for ordRec in ordRecords6:             
                    item_id=str(ordRec.item_id).strip().upper()
                    
                    item_qty_value=int(ordRec.quantity)
                    price=float(ordRec.ret_price)
                    item_vat=float(ordRec.ret_item_vat)
                    ret_rowid=ordRec.ret_rowid
                    
                    #-----------
                    bonus_qty=0
                    totalAmountTP+=round(item_qty_value*price,2)
                    totalAmountVat+=round(item_qty_value*item_vat,2)
                     
                    #------------ set batch id after checking stock
                    newBaseQty=item_qty_value                    
                    detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
                    detailList.append(detailDict)  
                     
                    #---------------------------------------                    
                    promoFlag=1
                    ordRec.update_record(rd_flag=1)
                     
            #------------ step-Last
            ordRecordsLast=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)&(db.sm_tp_rules_temp_return.fr_flag==0)&(db.sm_tp_rules_temp_return.di_flag==0)&(db.sm_tp_rules_temp_return.rd_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
            for ordRec in ordRecordsLast:
                item_id=str(ordRec.item_id).strip().upper()                
                item_qty_value=int(ordRec.quantity)
                price=float(ordRec.ret_price)   
                item_vat=float(ordRec.ret_item_vat)
                ret_rowid=ordRec.ret_rowid
                 
                bonus_qty=0                
                totalAmountTP+=round(item_qty_value*price,2)
                totalAmountVat+=round(item_qty_value*item_vat,2)            
                
                #------------ set batch id after checking stock
                newBaseQty=item_qty_value
                 
                detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
                detailList.append(detailDict)
                 
                #---------------------------------------
                 
    discount=round(float(discount),2)
    totalAmount=(round(totalAmountTP,2)+round(totalAmountVat,2)-discount)
    
    retMsg=''
    #=============== Insert invoice head and details
    if len(detailList) > 0:
        for j in range(len(detailList)):
            detailDictData=detailList[j]
            detailDictData['discount']=discount
            
        #-------------
        #Update status of head and detail       
         
        db((db.sm_tp_rules_temp_return_invoice.cid==c_id) & (db.sm_tp_rules_temp_return_invoice.depot_id==depot_id) &(db.sm_tp_rules_temp_return_invoice.return_sl==return_sl)).delete()
        rows=db.sm_tp_rules_temp_return_invoice.bulk_insert(detailList)
        
        retMsg='Processed Successfully'
        db.commit()
        
    #-------------- end order    
    return retMsg
    

# def old_get_rules_return(cid,depot_id,return_sl,invoice_sl,clientId,orderDate):
#     c_id=cid
#     depot_id=depot_id
#     sl=return_sl
#     client_id=clientId
#     orderDate=orderDate
#     
#     #========================-get settings flag
#     invoiceRulesFlag=False
#      
#     compSttRows=db((db.sm_settings.cid==c_id)&(db.sm_settings.s_key=='INVOICE_RULES')&(db.sm_settings.s_value=='YES')).select(db.sm_settings.cid,limitby=(0,1))
#     if compSttRows:
#         invoiceRulesFlag=True
#          
#     #================ if invoice rules are to apply (Note: ANY or Sepcific item, at a time two rules not applicable)
#     productBonusPriorityRows=''
#     approvedItemRows=''    
#     productBonusRows=''
#     specialRateRows=''
#     flatRateRows=''
#     promo_ref=0 #0=No,1=Yes
#     if invoiceRulesFlag==True:        
#         orderHeadRow=db((db.sm_invoice_head.cid==c_id) & (db.sm_invoice_head.depot_id==depot_id) & (db.sm_invoice_head.sl==invoice_sl)).select(db.sm_invoice_head.promo_ref,limitby=(0,1))
#         if orderHeadRow:
#             promo_ref=orderHeadRow[0].promo_ref
#             if promo_ref!=0:
#                 promo_ref=1
#         
#         approvedItemRows=db((db.sm_promo_approved_rate.cid==c_id)&(db.sm_promo_approved_rate.client_id==client_id)&(db.sm_promo_approved_rate.from_date<=orderDate)&(db.sm_promo_approved_rate.to_date>=orderDate)&(db.sm_promo_approved_rate.status=='ACTIVE')).select(db.sm_promo_approved_rate.product_id,db.sm_promo_approved_rate.bonus_type,db.sm_promo_approved_rate.fixed_percent_rate,orderby=~db.sm_promo_approved_rate.from_date|db.sm_promo_approved_rate.product_id)
#         productBonusRows=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,orderby=~db.sm_promo_product_bonus.min_qty)       #&(db.sm_promo_product_bonus.id!=promo_ref)
#         specialRateRows=db((db.sm_promo_special_rate.cid==c_id)&(db.sm_promo_special_rate.from_date<=orderDate)&(db.sm_promo_special_rate.to_date>=orderDate)&(db.sm_promo_special_rate.status=='ACTIVE')).select(db.sm_promo_special_rate.product_id,db.sm_promo_special_rate.min_qty,db.sm_promo_special_rate.special_rate_tp,db.sm_promo_special_rate.special_rate_vat,orderby=~db.sm_promo_special_rate.from_date)
#         flatRateRows=db((db.sm_promo_flat_rate.cid==c_id)&(db.sm_promo_flat_rate.from_date<=orderDate)&(db.sm_promo_flat_rate.to_date>=orderDate)&(db.sm_promo_flat_rate.status=='ACTIVE')).select(db.sm_promo_flat_rate.product_id,db.sm_promo_flat_rate.min_qty,db.sm_promo_flat_rate.flat_rate,orderby=~db.sm_promo_flat_rate.from_date)
#          
#     #----------- get delivery max sl from depot
#      
#     maxSl=return_sl
#      
#     records=''
#     #---------------   order detail records
#                                    
#     detailDict={}
#     detailList=[]                            
#          
#     totalAmountTP=0
#     totalAmountVat=0
#     discount=0    
#     discount_precent=0
#     #order details loop      
#     orderRecords=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)).select(db.sm_tp_rules_temp_return.ALL,limitby=(0,1))
#     if orderRecords:        
#         return_sl=orderRecords[0].return_sl        
#         invoice_sl=orderRecords[0].invoice_sl
#          
#         emptyBatchFlag=0
#         if invoiceRulesFlag==False:
#             #=========================== Rules not apply
#             retMsg='Rules not applicable'
#             return retMsg
#         else:
#             #===================== Rules apply 
#             promoFlag=0
#             totalAmt=0
#              
#             #-------- step-0: Priority (Product Bonus) 
#             #Not used
#              
#             if promo_ref==0:
#                 #-------- step-1: Approved rate            
#                 ordRecords1=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
#                 for ordRec in ordRecords1:             
#                     item_id=str(ordRec.item_id).strip().upper()                    
#                     item_qty_value=int(ordRec.quantity)
#                     price=float(ordRec.ret_price)   
#                     item_vat=float(ordRec.ret_item_vat)                    
#                     ret_rowid=ordRec.ret_rowid
#                      
#                     for appItemRow in approvedItemRows:
#                         product_id=str(appItemRow.product_id).strip().upper()
#                         bonus_type=appItemRow.bonus_type
#                         fixed_percent_rate=appItemRow.fixed_percent_rate
#                          
#                         if product_id==item_id:                            
#                             newPrice=0
#                             if bonus_type=='Fixed':
#                                 newPrice=fixed_percent_rate                                
#                             elif bonus_type=='Percentage':
#                                 newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
#                              
#                             #-----------
#                             bonus_qty=0                        
#                             totalAmountTP+=round(item_qty_value*newPrice,2)
#                             totalAmountVat+=round(item_qty_value*item_vat,2)                
#                              
#                             newBaseQty=item_qty_value
#                             #------------ set batch id after checking stock                            
#                             detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat}
#                             detailList.append(detailDict)                        
#                              
#                             #---------------------------------------                            
#                             promoFlag=1                        
#                             ordRec.update_record(ar_flag=1)
#                             break
#              
#             #-------- step-2: Product Bonus
#             for prodBonusRow in productBonusRows:      
#                 rowid=prodBonusRow.id
#                 circular_number=prodBonusRow.circular_number
#                 min_qty=prodBonusRow.min_qty
#                  
#                 pbQset=db((db.sm_promo_product_bonus_products.cid==c_id)&(db.sm_promo_product_bonus_products.refrowid==rowid)&(db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_promo_product_bonus_products.product_id==db.sm_tp_rules_temp_return.item_id))
#                 totalQtyRows=pbQset.select(db.sm_tp_rules_temp_return.quantity.sum(),groupby=db.sm_tp_rules_temp_return.cid)
#                  
#                 if totalQtyRows:
#                     qtyCount=totalQtyRows[0][db.sm_tp_rules_temp_return.quantity.sum()]
#                      
#                     if qtyCount>=min_qty:                        
#                         fullCount=int(qtyCount/min_qty)
#                          
#                         #===================================== for bonus calculate
#                         circularStr=circular_number
#                          
#                         nextQtyCount=qtyCount-min_qty*fullCount
#                          
#                         regularQty=0
#                         discountRate=0
#                          
#                         itemFullQty=min_qty*fullCount
#                          
#                         bonusDictList=[]
#                         bonusDictList.append({'rowid':rowid,'fullCount':fullCount,'circularNo':circular_number})
#                          
#                         if nextQtyCount>0:
#                             prodPromList=[]
#                             totalItemRows=pbQset.select(db.sm_tp_rules_temp_return.item_id,groupby=db.sm_tp_rules_temp_return.item_id)
#                             for totItemRow in totalItemRows:                            
#                                 prodPromList.append(totItemRow.item_id)
#                                  
#                             productBonusRows2=db((db.sm_promo_product_bonus.cid==c_id)&(db.sm_promo_product_bonus.from_date<=orderDate)&(db.sm_promo_product_bonus.to_date>=orderDate)&(db.sm_promo_product_bonus.status=='ACTIVE')&(db.sm_promo_product_bonus.id!=rowid)&(db.sm_promo_product_bonus.id==db.sm_promo_product_bonus_products.refrowid)&(db.sm_promo_product_bonus_products.product_id.belongs(prodPromList))).select(db.sm_promo_product_bonus.id,db.sm_promo_product_bonus.circular_number,db.sm_promo_product_bonus.min_qty,orderby=~db.sm_promo_product_bonus.min_qty,groupby=db.sm_promo_product_bonus.id)
#                             if productBonusRows2:                            
#                                 for productBonusRow2 in productBonusRows2:      
#                                     rowid2=productBonusRow2.id
#                                     circular_number2=productBonusRow2.circular_number
#                                     min_qty2=productBonusRow2.min_qty
#                                      
#                                     if nextQtyCount>=min_qty2:
#                                         fullCount2=int(nextQtyCount/min_qty2)
#                                          
#                                         circularStr+=','+str(circular_number2)
#                                         bonusDictList.append({'rowid':rowid2,'fullCount':fullCount2,'circularNo':circular_number2})
#                                          
#                                         nextQtyCount=nextQtyCount-min_qty2*fullCount2
#                                         itemFullQty+=min_qty2*fullCount2
#                                                
#                                     else:                                        
#                                         break
#                                          
#                                 if nextQtyCount>0:
#                                     regularQty=nextQtyCount
#                                     #discount apply
#                             else:
#                                 regularQty=nextQtyCount
#                                 #discount apply
#                                  
#                         #------ insert and update flag
#                         ordRecords2=pbQset.select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
#                         for ordRec in ordRecords2:
#                             item_id=str(ordRec.item_id).strip().upper()                            
#                             item_qty_value=int(ordRec.quantity)
#                             price=float(ordRec.ret_price)   
#                             item_vat=float(ordRec.ret_item_vat)
#                             ret_rowid=ordRec.ret_rowid
#                              
#                             #-----------
#                             bonus_qty=0                            
#                             totalAmountTP+=round(item_qty_value*price,2)
#                             totalAmountVat+=round(item_qty_value*item_vat,2)
#                              
#                             #----------- new code
#                             declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
#                             if not declaredItemRow:
#                                 discountRate=price
#                                 #regular rate, applied discount
#                              
#                             #------------ set batch id after checking stock
#                             newBaseQty=item_qty_value
#                              
#                             detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
#                             detailList.append(detailDict)  
#                              
#                             #--------------------------------------
#                             promoFlag=1
#                             ordRec.update_record(pb_flag=1)
#                              
#                         #new code
#                         #product bonus rest qty discount apply                        
#                         totalAmt+=round(regularQty*discountRate,2)
#                          
#                         #--------- bonus item insert                        
#                         for k in range(len(bonusDictList)):
#                             bonusDictData=bonusDictList[k]
#                              
#                             bRowid=bonusDictData['rowid']
#                             bfullCount=bonusDictData['fullCount']
#                             bcircularNo=bonusDictData['circularNo']
#                             #end new code next use bRowid
#                              
#                             #--------- bonus item add
#                             bonusRows=db((db.sm_promo_product_bonus_bonuses.cid==c_id)&(db.sm_promo_product_bonus_bonuses.refrowid==bRowid)&(db.sm_item.cid==c_id)&(db.sm_item.item_id==db.sm_promo_product_bonus_bonuses.bonus_product_id)).select(db.sm_promo_product_bonus_bonuses.bonus_product_id,db.sm_item.name,db.sm_item.category_id,db.sm_item.category_id_sp,db.sm_item.unit_type,db.sm_item.item_carton,db.sm_promo_product_bonus_bonuses.bonus_qty)
#                             for bonusRow in bonusRows:
#                                 bonus_product_id=bonusRow.sm_promo_product_bonus_bonuses.bonus_product_id                                
#                                 bonus_item_qty=bonusRow.sm_promo_product_bonus_bonuses.bonus_qty                            
#                                  
#                                 ret_rowid=0
#                                  
#                                 #----
#                                 item_id=bonus_product_id
#                                  
#                                 item_qty_value=0
#                                 bonus_qty=bonus_item_qty*bfullCount
#                                 newPrice=0
#                                 item_vat=0
#                                  
#                                 newBaseQty=bonus_qty
#                                 #------------ set batch id after checking stock
#                                 detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':item_qty_value,'bonus_qty':newBaseQty,'price':newPrice,'item_vat':item_vat}
#                                 detailList.append(detailDict)
#                                  
#                                 #----------------------------                              
#                                 promoFlag=1
#                              
#                         #break                
#                     #------------
#              
#             #-------- step-3: Special rate
#             ordRecords3=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
#             for ordRec in ordRecords3:             
#                 item_id=str(ordRec.item_id).strip().upper()                
#                 item_qty_value=int(ordRec.quantity)
#                 price=float(ordRec.ret_price)
#                 item_vat=float(ordRec.ret_item_vat)
#                 ret_rowid=ordRec.ret_rowid
#                  
#                 for spRateRow in specialRateRows:
#                     product_id=str(spRateRow.product_id).strip().upper()
#                     min_qty=spRateRow.min_qty
#                     special_rate_tp=spRateRow.special_rate_tp
#                     special_rate_vat=spRateRow.special_rate_vat
#                      
#                     if product_id==item_id and item_qty_value>=min_qty:
#                         newPrice=special_rate_tp
#                         newVat=special_rate_vat                        
#                          
#                         #-----------
#                         bonus_qty=0                        
#                         totalAmountTP+=round(item_qty_value*newPrice,2)
#                         totalAmountVat+=round(item_qty_value*item_vat,2)
#                          
#                         #------------ set batch id after checking stock
#                         newBaseQty=item_qty_value
#                         detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':newVat}
#                         detailList.append(detailDict)
#                          
#                         #---------------------------------------                        
#                         promoFlag=1                        
#                         ordRec.update_record(sr_flag=1)
#                         break
#                          
#             #-------- step-4: Flat rate            
#             ordRecords4=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
#             for ordRec in ordRecords4:             
#                 item_id=str(ordRec.item_id).strip().upper()                
#                 item_qty_value=int(ordRec.quantity)
#                 price=float(ordRec.ret_price)
#                 item_vat=float(ordRec.ret_item_vat)
#                 ret_rowid=ordRec.ret_rowid
#                  
#                 for flatRateRow in flatRateRows:
#                     product_id=str(flatRateRow.product_id).strip().upper()
#                     min_qty=flatRateRow.min_qty
#                     flat_rate=flatRateRow.flat_rate
#                      
#                     if product_id==item_id and item_qty_value>=min_qty:
#                         regularQty=(item_qty_value%min_qty)
#                         fullQty=item_qty_value-regularQty
#                          
#                         newPrice=flat_rate                                               
#                          
#                         #-----------
#                         bonus_qty=0
#                          
#                         totalAmountTP+=round(fullQty*newPrice,2)
#                         totalAmountVat+=round(fullQty*item_vat,2)
#                                                  
#                         #------------ set batch id after checking stock
#                         newBaseQty=fullQty
#                          
#                         detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat}
#                         detailList.append(detailDict)
#                          
#                         #---------------------------------------                        
#                         if regularQty>0:                                                                        
#                              
#                             #-----------
#                             bonus_qty=0                            
#                             totalAmountTP+=round(regularQty*price,2)
#                             totalAmountVat+=round(regularQty*item_vat,2)
#                              
#                             #-----------
#                             declaredItemRow=db((db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.product_id==item_id)&(db.sm_promo_declared_item.status=='ACTIVE')).select(db.sm_promo_declared_item.id,limitby=(0,1))
#                             if not declaredItemRow:
#                                 totalAmt+=round(regularQty*price,2)
#                              
#                             #------------ set batch id after checking stock
#                             newBaseQty=regularQty
#                              
#                             detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
#                             detailList.append(detailDict)                            
#                             #---------------------------------------
#                          
#                         promoFlag=1                        
#                         ordRec.update_record(fr_flag=1)
#                         break
#             #-------- promo ref=1 then aproved rate later
#             if promo_ref==1:
#                 #-------- step-1: Approved rate            
#                 ordRecords1=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)&(db.sm_tp_rules_temp_return.fr_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
#                 for ordRec in ordRecords1:             
#                     item_id=str(ordRec.item_id).strip().upper()                    
#                     item_qty_value=int(ordRec.quantity)
#                     price=float(ordRec.ret_price)   
#                     item_vat=float(ordRec.ret_item_vat)
#                     ret_rowid=ordRec.ret_rowid
#                      
#                     for appItemRow in approvedItemRows:
#                         product_id=str(appItemRow.product_id).strip().upper()
#                         bonus_type=appItemRow.bonus_type
#                         fixed_percent_rate=appItemRow.fixed_percent_rate
#                          
#                         if product_id==item_id:                            
#                             newPrice=0
#                             if bonus_type=='Fixed':
#                                 newPrice=fixed_percent_rate                                
#                             elif bonus_type=='Percentage':
#                                 newPrice=price-round((price*fixed_percent_rate)/100,2) #discount percent
#                                  
#                             #-----------
#                             bonus_qty=0                        
#                             totalAmountTP+=round(item_qty_value*newPrice,2)
#                             totalAmountVat+=round(item_qty_value*item_vat,2)                
#                              
#                             newBaseQty=item_qty_value
#                             #------------ set batch id after checking stock                            
#                             detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':newPrice,'item_vat':item_vat}
#                             detailList.append(detailDict)                        
#                              
#                             #---------------------------------------                            
#                             promoFlag=1                        
#                             ordRec.update_record(ar_flag=1)
#                             break
#              
#             #-------- step-5: Declared Item           
#             ordRecords5=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)&(db.sm_tp_rules_temp_return.fr_flag==0)&(db.sm_promo_declared_item.cid==c_id)&(db.sm_promo_declared_item.status=='ACTIVE')&(db.sm_tp_rules_temp_return.item_id==db.sm_promo_declared_item.product_id)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
#             for ordRec in ordRecords5:             
#                 item_id=str(ordRec.item_id).strip().upper()                
#                 item_qty_value=int(ordRec.quantity)
#                 price=float(ordRec.ret_price)
#                 item_vat=float(ordRec.ret_item_vat)                
#                 ret_rowid=ordRec.ret_rowid
#                  
#                 #-----------
#                 bonus_qty=0
#                 totalAmountTP+=round(item_qty_value*price,2)
#                 totalAmountVat+=round(item_qty_value*item_vat,2)
#                  
#                 #------------ set batch id after checking stock
#                 newBaseQty=item_qty_value
#                  
#                 detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
#                 detailList.append(detailDict)
#                  
#                 #---------------------------------------                
#                 promoFlag=1                        
#                 ordRec.update_record(di_flag=1)
#                  
#             #-------- step-6: Regular Discount            
#             ordRec6Qset=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)&(db.sm_tp_rules_temp_return.fr_flag==0)&(db.sm_tp_rules_temp_return.di_flag==0))
#             ordRec6Rows=ordRec6Qset.select(db.sm_tp_rules_temp_return.quantity,db.sm_tp_rules_temp_return.ret_price,db.sm_tp_rules_temp_return.ret_item_vat)
#             if ordRec6Rows:
#                 #totalAmt=0                
#                 for ordRec6Row in ordRec6Rows:             
#                     quantity=ordRec6Row.quantity
#                     price=ordRec6Row.ret_price
#                     #item_vat=ordRec6Row.item_vat                    
#                     totalAmt+=quantity*price
#             # discount calculation
#             discountRows=db((db.sm_promo_regular_discount.cid==c_id)&(db.sm_promo_regular_discount.from_date<=orderDate)&(db.sm_promo_regular_discount.to_date>=orderDate) & (db.sm_promo_regular_discount.status=='ACTIVE')&(db.sm_promo_regular_discount.min_amount<=totalAmt)).select(db.sm_promo_regular_discount.discount_precent,orderby=~db.sm_promo_regular_discount.min_amount,limitby=(0,1))
#             if discountRows:
#                 discount_precent=discountRows[0].discount_precent
#                  
#                 discount=round((totalAmt*discount_precent)/100,2)
#                  
#                 ordRecords6=ordRec6Qset.select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
#                 for ordRec in ordRecords6:             
#                     item_id=str(ordRec.item_id).strip().upper()
#                      
#                     item_qty_value=int(ordRec.quantity)
#                     price=float(ordRec.ret_price)
#                     item_vat=float(ordRec.ret_item_vat)
#                     ret_rowid=ordRec.ret_rowid
#                      
#                     #-----------
#                     bonus_qty=0
#                     totalAmountTP+=round(item_qty_value*price,2)
#                     totalAmountVat+=round(item_qty_value*item_vat,2)
#                      
#                     #------------ set batch id after checking stock
#                     newBaseQty=item_qty_value
#                      
#                     detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
#                     detailList.append(detailDict)  
#                      
#                     #---------------------------------------                    
#                     promoFlag=1
#                     ordRec.update_record(rd_flag=1)
#                      
#             #------------ step-Last
#             ordRecordsLast=db((db.sm_tp_rules_temp_return.cid==c_id) & (db.sm_tp_rules_temp_return.depot_id==depot_id)&(db.sm_tp_rules_temp_return.return_sl==return_sl)&(db.sm_tp_rules_temp_return.prio_flag==0)&(db.sm_tp_rules_temp_return.ar_flag==0)&(db.sm_tp_rules_temp_return.pb_flag==0)&(db.sm_tp_rules_temp_return.sr_flag==0)&(db.sm_tp_rules_temp_return.fr_flag==0)&(db.sm_tp_rules_temp_return.di_flag==0)&(db.sm_tp_rules_temp_return.rd_flag==0)).select(db.sm_tp_rules_temp_return.ALL,orderby=db.sm_tp_rules_temp_return.item_id)
#             for ordRec in ordRecordsLast:
#                 item_id=str(ordRec.item_id).strip().upper()                
#                 item_qty_value=int(ordRec.quantity)
#                 price=float(ordRec.ret_price)   
#                 item_vat=float(ordRec.ret_item_vat)
#                 ret_rowid=ordRec.ret_rowid
#                  
#                 bonus_qty=0                
#                 totalAmountTP+=round(item_qty_value*price,2)
#                 totalAmountVat+=round(item_qty_value*item_vat,2)            
#                  
#                 #------------ set batch id after checking stock
#                 newBaseQty=item_qty_value
#                  
#                 detailDict={'cid':c_id,'depot_id':depot_id,'return_sl':return_sl,'invoice_sl':invoice_sl,'ret_rowid':ret_rowid,'discount':0,'item_id':item_id,'quantity':newBaseQty,'bonus_qty':bonus_qty,'price':price,'item_vat':item_vat}
#                 detailList.append(detailDict)
#                  
#                 #---------------------------------------
#                  
#     discount=round(float(discount),2)
#     totalAmount=(round(totalAmountTP,2)+round(totalAmountVat,2)-discount)
#      
#     retMsg=''
#     #=============== Insert invoice head and details
#     if len(detailList) > 0:
#          
#         for j in range(len(detailList)):
#             detailDictData=detailList[j]
#             detailDictData['discount']=discount
#          
#         #-------------
#         #Update status of head and detail       
#          
#         db((db.sm_tp_rules_temp_return_invoice.cid==c_id) & (db.sm_tp_rules_temp_return_invoice.depot_id==depot_id) &(db.sm_tp_rules_temp_return_invoice.return_sl==return_sl)).delete()
#         rows=db.sm_tp_rules_temp_return_invoice.bulk_insert(detailList)
#          
#         retMsg='Processed Successfully'
#         db.commit()
#          
#     #-------------- end order    
#     return retMsg
    

# Create Invoice from Order to Delivery with Invoiced status 
def bak_get_order_to_delivery(cid,depot_id,order_sl,clientId,orderDate):
    c_id=cid
    depot_id=depot_id
    sl=order_sl
    client_id=clientId
    orderDate=orderDate
    
    #========================-get settings flag
    invoiceRulesFlag=False
    #    partigalStockFlag=False
    #    negativeStockFlag=False
    #    restrictedStockFlag=False
    
    compSttRows=db(db.sm_settings.cid==c_id).select(db.sm_settings.cid,db.sm_settings.s_key,db.sm_settings.s_value)
    for sttRow in compSttRows:
        s_key=str(sttRow.s_key).strip().upper()
        s_value=str(sttRow.s_value).strip()
        
        if (s_key=='INVOICE_RULES' and s_value=='YES'):
            invoiceRulesFlag=True
            break                  
    #    elif (s_key=='PARTIAL_DELIVERY' and s_value=='YES'):
    #        partigalStockFlag=True
    #    elif (s_key=='NEGETIVE_STOCK' and s_value=='YES'):
    #        negativeStockFlag=True
    #    elif (s_key=='RESTRICTED_STOCK' and s_value=='YES'):
    #        restrictedStockFlag=True    
    compSttRows=''
        
    #================ if invoice rules are to apply (Note: ANY or Sepcific item, at a time two rules not applicable)
    specificItemFlag=False
    anyItemFlag=False  
    if invoiceRulesFlag==True:                        
        #---------- check invoice rules category 
        invRulesRows=''
        invRulesRows=db((db.sm_tpcp_rules.cid==c_id)&((db.sm_tpcp_rules.from_date<=orderDate)&(db.sm_tpcp_rules.to_date>=orderDate))&(db.sm_tpcp_rules.status=='ACTIVE')).select(db.sm_tpcp_rules.ALL,orderby=~db.sm_tpcp_rules.id)
        
        for invRow in invRulesRows:
            itemFor=str(invRow.for_any_item).strip().upper()                          
            if (itemFor=='ANY'):
                anyItemFlag=True
                specificItemFlag=False
                break
            elif (itemFor!='ANY'):
                specificItemFlag=True
        
        #------------ restricted stock records
        # use write here
    
    #---------- get client category for invoice rules
    clientCategory=''
    if (invoiceRulesFlag==True and (anyItemFlag==True or specificItemFlag==True)):
        clientRecords=db((db.sm_client.cid==c_id)&(db.sm_client.depot_id==depot_id)&(db.sm_client.client_id==client_id)).select(db.sm_client.category_id,limitby=(0,1))
        if clientRecords:
            clientCategory=clientRecords[0].category_id
    
    #----------- get delivery max sl from depot
    maxSl=1
    records=db((db.sm_depot.cid==c_id) & (db.sm_depot.depot_id==depot_id)).select(db.sm_depot.id,db.sm_depot.del_sl,limitby=(0,1))
    if records:
        dsl=records[0].del_sl
        maxSl=int(dsl)+1
    
    #--- sl update in depot
    records[0].update_record(del_sl=maxSl)
    records=''
    #---------------   order detail records
    depot_name=''
    client_id=''
    client_name=''
    rep_id=''
    rep_name=''
    area_id=''
    area_name=''
    order_datetime=''
    payment_mode=''
    req_note=''
    ym_date=''
    req_delivery_date=''
    
    #----------------
    headDict={}   
    headList=[]                                               
    detailDict={}
    detailList=[]                            
    headFlag=False
                              
    totalAmount=0
    discount=0    
    
    #order details loop                        
    orderRecords=db((db.sm_order.cid==c_id) & (db.sm_order.depot_id==depot_id) &(db.sm_order.sl==sl)&(db.sm_order.status=='Submitted')).select(db.sm_order.ALL,orderby=db.sm_order.item_name)
    for row in orderRecords:                                
        rowId=row.id     
        depot_id=row.depot_id
        depot_name=row.depot_name
        client_id=row.client_id
        client_name=row.client_name
        rep_id=row.rep_id
        rep_name=row.rep_name
        area_id=row.area_id
        area_name=row.area_name                                
        order_datetime=row.order_datetime
        payment_mode=row.payment_mode                            
        req_note=row.note                                
        item_id=str(row.item_id).strip().upper()
        item_name=row.item_name
        category_id=row.category_id
        item_qty_value=int(row.quantity)
        price=float(row.price)                                
        #----- delivery date get from order date
        ym_date=str(order_datetime)[0:7]+'-01'
        req_delivery_date=str(order_datetime)[0:10]
        
        bonus_qty=0
        itemTotal=price*item_qty_value                                
        totalAmount+=itemTotal
        
        short_note=''
        
        #=============== invoice rules check for specific item ; bonus qty no problem, discout+=discount
        if (invoiceRulesFlag==True and anyItemFlag==False and specificItemFlag==True):                                
            for invRow in invRulesRows:
                client_category=str(invRow.client_cat).strip()
                dateFrom=invRow.from_date
                dateTo=invRow.to_date
                itemFor=str(invRow.for_any_item).strip().upper()
                limitFrom=invRow.from_amt_qty
                limitTo=invRow.to_amt_qty
                bonusType=invRow.bonus_type
                                
                b_item_id1=str(invRow.b_item_id1).strip().upper()
                b_item_id2=str(invRow.b_item_id2).strip().upper()
                b_item_id3=str(invRow.b_item_id3).strip().upper()
                
                b_item_qty1=invRow.b_item_qty1
                b_item_qty2=invRow.b_item_qty2
                b_item_qty3=invRow.b_item_qty3
                
                bonus_disc_qty_amt_per=float(invRow.disc_amt_per)
                
                #--------- bonus qty for per(from==to)limited  qty; discAmt and discPer not allowed
                if  ((client_category=='ALL' or client_category==clientCategory) and (orderDate>=dateFrom and orderDate<=dateTo) and itemFor==item_id and limitFrom==limitTo):
                    if (bonusType=='Item'):
                        
                        #======== bonus Item 1
                        if not (b_item_id1=='' or b_item_id1==None):
                            if (item_id==b_item_id1):
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonus_qty=qtySlap*int(b_item_qty1)
                                short_note='bonus %s'%(bonus_qty)
                                
                            else:
                                itemId=''
                                itemName=''
                                categoryId=''
                                itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id1)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                if itemRows:
                                    itemId=itemRows[0].item_id
                                    itemName=itemRows[0].name
                                    categoryId=itemRows[0].category_id
                                
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonusQty=qtySlap*int(b_item_qty1)
                                
                                short_note='bonus item %s (%s)'%(itemId,bonusQty)   # used main item
                                shortNote='bonus for %s'%(item_id)                  # used bonus new item
                                #------------
                                if bonusQty!=0:
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                   'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                    detailList.append(detailDict)                                            
                    
                        #======== bonus Item 2
                        if not (b_item_id2=='' or b_item_id2==None):
                            if (item_id==b_item_id2):
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonus_qty=qtySlap*int(b_item_qty2)
                                short_note='bonus %s'%(bonus_qty)
                                
                            else:
                                itemId=''
                                itemName=''
                                categoryId=''
                                itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id2)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                if itemRows:
                                    itemId=itemRows[0].item_id
                                    itemName=itemRows[0].name
                                    categoryId=itemRows[0].category_id
                                
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonusQty=qtySlap*int(b_item_qty2)
                                
                                short_note='bonus item %s (%s)'%(itemId,bonusQty)   # used main item
                                shortNote='bonus for %s'%(item_id)                  # used bonus new item
                                #------------
                                if bonusQty!=0:
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                   'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                    detailList.append(detailDict)
                        
                        #======== bonus Item 3
                        if not (b_item_id3=='' or b_item_id3==None):
                            if (item_id==b_item_id3):
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonus_qty=qtySlap*int(b_item_qty3)
                                short_note='bonus %s'%(bonus_qty)
                                
                            else:
                                itemId=''
                                itemName=''
                                categoryId=''
                                itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id3)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                if itemRows:
                                    itemId=itemRows[0].item_id
                                    itemName=itemRows[0].name
                                    categoryId=itemRows[0].category_id
                                
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonusQty=qtySlap*int(b_item_qty3)
                                
                                short_note='bonus item %s (%s)'%(itemId,bonusQty)   # used main item
                                shortNote='bonus for %s'%(item_id)                  # used bonus new item
                                #------------
                                if bonusQty!=0:
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                   'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                    detailList.append(detailDict)
                        break           
                        
                #---------------within range. discount percent,discout amt,bonus qty
                else:
                    if ((client_category=='ALL' or client_category==clientCategory) and (orderDate>=dateFrom and orderDate<=dateTo) and itemFor==item_id and (item_qty_value>=limitFrom and item_qty_value<=limitTo)): 
                        if bonusType=='DiscPer':
                            disAmt=(itemTotal*bonus_disc_qty_amt_per)/100
                            discount+=disAmt
                            short_note='discount %s'%(round(float(disAmt),2))
                            break                                          
                        elif bonusType=='DiscAmt':
                            disAmt=bonus_disc_qty_amt_per
                            discount+=disAmt
                            short_note='discount %s'%(round(float(disAmt),2))
                            break
                        elif bonusType=='Item':
                            #======== bonus Item 1
                            if not (b_item_id1=='' or b_item_id1==None):
                                if (item_id==b_item_id1):
                                    bonus_qty=int(b_item_qty1)
                                    short_note='bonus %s'%(bonus_qty)                                    
                                else:
                                    itemId=''
                                    itemName=''
                                    categoryId=''
                                    itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id1)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                    if itemRows:
                                        itemId=itemRows[0].item_id
                                        itemName=itemRows[0].name
                                        categoryId=itemRows[0].category_id
                                    
                                    bonusQty=int(b_item_qty1)
                                    
                                    short_note='bonus item %s (%s)'%(itemId,bonusQty)  # used main item
                                    shortNote='bonus for %s'%(item_id)                 # used bonus new item
                                    #------------
                                    if bonusQty!=0:
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                       'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                        detailList.append(detailDict)                                            
                            
                            #======== bonus Item 2
                            if not (b_item_id2=='' or b_item_id2==None):
                                if (item_id==b_item_id2):
                                    bonus_qty=int(b_item_qty2)
                                    short_note='bonus %s'%(bonus_qty)                                    
                                else:
                                    itemId=''
                                    itemName=''
                                    categoryId=''
                                    itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id2)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                    if itemRows:
                                        itemId=itemRows[0].item_id
                                        itemName=itemRows[0].name
                                        categoryId=itemRows[0].category_id
                                    
                                    bonusQty=int(b_item_qty2)
                                    
                                    short_note='bonus item %s (%s)'%(itemId,bonusQty)  # used main item
                                    shortNote='bonus for %s'%(item_id)                 # used bonus new item
                                    #------------
                                    if bonusQty!=0:
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                       'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                        detailList.append(detailDict)                                            
                            
                            #======== bonus Item 3
                            if not (b_item_id3=='' or b_item_id3==None):
                                if (item_id==b_item_id3):
                                    bonus_qty=int(b_item_qty3)
                                    short_note='bonus %s'%(bonus_qty)                                    
                                else:
                                    itemId=''
                                    itemName=''
                                    categoryId=''
                                    itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id3)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                    if itemRows:
                                        itemId=itemRows[0].item_id
                                        itemName=itemRows[0].name
                                        categoryId=itemRows[0].category_id
                                    
                                    bonusQty=int(b_item_qty3)
                                    
                                    short_note='bonus item %s (%s)'%(itemId,bonusQty)  # used main item
                                    shortNote='bonus for %s'%(item_id)                 # used bonus new item
                                    #------------
                                    if bonusQty!=0:
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                       'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                        detailList.append(detailDict)                                            
                            break
                        
        #------ get current stock balance for a specific item
        #       totalReqQty=item_qty_value+bonus_qty        
        # here will be checked restricted stock item        
        # here will be checked negative stock allowed or not
        
        #------------
        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                       'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':item_id,'item_name':item_name,'category_id':category_id,'quantity':item_qty_value,'bonus_qty':bonus_qty,'price':price,'ym_date':ym_date,'short_note':short_note}
        detailList.append(detailDict)
        if headFlag==False:
            headDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                       'area_id':area_id,'area_name':area_name,'status':'Invoiced','ym_date':ym_date}
            headList.append(headDict)
            headFlag=True
    
    #end one order details loop
    orderRecords=''
    
    #=================invoice rules for total amount
    if (invoiceRulesFlag==True and anyItemFlag==True and specificItemFlag==False):                                
        for invRow in invRulesRows:
            client_category=str(invRow.client_cat).strip()
            dateFrom=invRow.from_date
            dateTo=invRow.to_date
            itemFor=str(invRow.for_any_item).strip().upper()
            limitFrom=invRow.from_amt_qty
            limitTo=invRow.to_amt_qty
            bonusType=invRow.bonus_type
            
            b_item_id1=str(invRow.b_item_id1).strip().upper()
            b_item_id2=str(invRow.b_item_id2).strip().upper()
            b_item_id3=str(invRow.b_item_id3).strip().upper()
            
            b_item_qty1=invRow.b_item_qty1
            b_item_qty2=invRow.b_item_qty2
            b_item_qty3=invRow.b_item_qty3
            
            bonus_disc_qty_amt_per=float(invRow.disc_amt_per)                                   
            if ((client_category=='ALL' or client_category==clientCategory) and (orderDate>=dateFrom and orderDate<=dateTo) and itemFor=='ANY' and (totalAmount>=limitFrom and totalAmount<=limitTo)): 
                if bonusType=='DiscPer':
                    discount=(totalAmount*bonus_disc_qty_amt_per)/100
                    break                                          
                elif bonusType=='DiscAmt':
                    discount=bonus_disc_qty_amt_per
                    break
                elif bonusType=='Item':
                    #======== bonus Item 1
                    if not (b_item_id1=='' or b_item_id1==None):                        
                        itemId=''
                        itemName=''
                        categoryId=''
                        itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id1)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                        if itemRows:
                            itemId=itemRows[0].item_id
                            itemName=itemRows[0].name
                            categoryId=itemRows[0].category_id
                        
                        bonusQty=b_item_qty1
                        shortNote='bonus for total amount'
                        #------------
                        if bonusQty!=0:
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                           'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                            detailList.append(detailDict)                                            
                    
                    #======== bonus Item 2
                    if not (b_item_id2=='' or b_item_id2==None):                        
                        itemId=''
                        itemName=''
                        categoryId=''
                        itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id2)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                        if itemRows:
                            itemId=itemRows[0].item_id
                            itemName=itemRows[0].name
                            categoryId=itemRows[0].category_id
                        
                        bonusQty=b_item_qty2
                        shortNote='bonus for total amount'
                        #------------
                        if bonusQty!=0:
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                           'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                            detailList.append(detailDict)
                    
                    #======== bonus Item 3
                    if not (b_item_id3=='' or b_item_id3==None):                        
                        itemId=''
                        itemName=''
                        categoryId=''
                        itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id3)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                        if itemRows:
                            itemId=itemRows[0].item_id
                            itemName=itemRows[0].name
                            categoryId=itemRows[0].category_id
                        
                        bonusQty=b_item_qty3
                        shortNote='bonus for total amount'
                        #------------
                        if bonusQty!=0:
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                           'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                            detailList.append(detailDict)
                    break
                    
                    
    #-----------------
    discount=round(float(discount),2)
    totalAmount=totalAmount-discount                            
    
    retMsg=''
    #=============== Insert invoice head and details
    if (len(headList)> 0 and len(detailList) > 0):
        #---------- dicount amount assigned
        for i in range(len(headList)):
            headDictData=headList[i]
            headDictData['discount']=discount
            
        for j in range(len(detailList)):
            detailDictData=detailList[j]
            detailDictData['discount']=discount
        
        #------------- call balance update function
        strData=str(c_id)+'<fdfd>DELIVERY<fdfd>'+str(maxSl)+'<fdfd>'+str(datetime_fixed)+'<fdfd>'+str(depot_id)+'-'+str(maxSl)+'<fdfd>DPT-'+str(depot_id)+'<fdfd>CLT-'+str(client_id)+'<fdfd>'+str(totalAmount)
        
        if strData!='':
            resStr=set_balance_transaction(strData)
            
            resStrList=resStr.split('<sep>',resStr.count('<sep>'))
            flag=resStrList[0]
            msg=resStrList[1]
            if flag=='True':
                #Update status of head and detail                
                rows=db.sm_invoice.bulk_insert(detailList)
                rows=db.sm_invoice_head.bulk_insert(headList)                        
                db((db.sm_order_head.cid==c_id) & (db.sm_order_head.depot_id==depot_id) & (db.sm_order_head.client_id==client_id)&(db.sm_order_head.sl==sl)).update(status='Invoiced',delivery_date=req_delivery_date,invoice_ref=maxSl,flag_data='1')
                db((db.sm_order.cid==c_id) & (db.sm_order.depot_id==depot_id) & (db.sm_order.client_id==client_id)&(db.sm_order.sl==sl)).update(status='Invoiced',delivery_date=req_delivery_date,invoice_ref=maxSl)
                retMsg='Successfully Imported'
                db.commit()
    
    #-------------- end order
    invRulesRows=''
    
    return retMsg+','+str(maxSl)
    
# Old system
# Create Invoice from Order to Delivery with Submitted status 
def bak_get_order_to_delivery_submit(cid,depot_id,order_sl,clientId,orderDate):
    c_id=cid
    depot_id=depot_id
    sl=order_sl
    client_id=clientId
    orderDate=orderDate
    
    #========================-get settings flag
    invoiceRulesFlag=False
    #    partigalStockFlag=False
    #    negativeStockFlag=False
    #    restrictedStockFlag=False
    
    compSttRows=db(db.sm_settings.cid==c_id).select(db.sm_settings.cid,db.sm_settings.s_key,db.sm_settings.s_value)
    for sttRow in compSttRows:
        s_key=str(sttRow.s_key).strip().upper()
        s_value=str(sttRow.s_value).strip()
        
        if (s_key=='INVOICE_RULES' and s_value=='YES'):
            invoiceRulesFlag=True
            break                  
    #    elif (s_key=='PARTIAL_DELIVERY' and s_value=='YES'):
    #        partigalStockFlag=True
    #    elif (s_key=='NEGETIVE_STOCK' and s_value=='YES'):
    #        negativeStockFlag=True
    #    elif (s_key=='RESTRICTED_STOCK' and s_value=='YES'):
    #        restrictedStockFlag=True    
    compSttRows=''
    
    #================ if invoice rules are to apply (Note: ANY or Sepcific item, at a time two rules not applicable)
    specificItemFlag=False
    anyItemFlag=False  
    if invoiceRulesFlag==True:                        
        #---------- check invoice rules category 
        invRulesRows=''
        invRulesRows=db((db.sm_tpcp_rules.cid==c_id)&((db.sm_tpcp_rules.from_date<=orderDate)&(db.sm_tpcp_rules.to_date>=orderDate))&(db.sm_tpcp_rules.status=='ACTIVE')).select(db.sm_tpcp_rules.ALL,orderby=~db.sm_tpcp_rules.id)
        for invRow in invRulesRows:
            itemFor=str(invRow.for_any_item).strip().upper()                          
            if (itemFor=='ANY'):
                anyItemFlag=True
                specificItemFlag=False
                break
            elif (itemFor!='ANY'):
                specificItemFlag=True
                
        #------------ restricted stock records
        # use write here
    
    #---------- get client category for invoice rules
    clientCategory=''
    if (invoiceRulesFlag==True and (anyItemFlag==True or specificItemFlag==True)):
        clientRecords=db((db.sm_client.cid==c_id)&(db.sm_client.depot_id==depot_id)&(db.sm_client.client_id==client_id)).select(db.sm_client.category_id,limitby=(0,1))
        if clientRecords:
            clientCategory=clientRecords[0].category_id
    
    #----------- get delivery max sl from depot
    maxSl=1
    records=db((db.sm_depot.cid==c_id) & (db.sm_depot.depot_id==depot_id)).select(db.sm_depot.id,db.sm_depot.del_sl,limitby=(0,1))
    if records:
        dsl=records[0].del_sl
        maxSl=int(dsl)+1
    
    #--- sl update in depot
    records[0].update_record(del_sl=maxSl)
    records=''
    #---------------   order detail records
    depot_name=''
    client_id=''
    client_name=''
    rep_id=''
    rep_name=''
    area_id=''
    area_name=''
    order_datetime=''
    payment_mode=''
    req_note=''
    ym_date=''
    req_delivery_date=''
    
    #----------------
    headDict={}   
    headList=[]                                               
    detailDict={}
    detailList=[]                            
    headFlag=False
                              
    totalAmount=0
    discount=0    
    
    #order details loop                        
    orderRecords=db((db.sm_order.cid==c_id) & (db.sm_order.depot_id==depot_id) &(db.sm_order.sl==sl)&(db.sm_order.status=='Submitted')).select(db.sm_order.ALL,orderby=db.sm_order.item_name)
    for row in orderRecords:                                
        rowId=row.id     
        depot_id=row.depot_id
        depot_name=row.depot_name
        client_id=row.client_id
        client_name=row.client_name
        rep_id=row.rep_id
        rep_name=row.rep_name
        area_id=row.area_id
        area_name=row.area_name                                
        order_datetime=row.order_datetime
        delivery_date=row.delivery_date
        
        payment_mode=row.payment_mode                            
        req_note=row.note                                
        item_id=str(row.item_id).strip().upper()
        item_name=row.item_name
        category_id=row.category_id
        item_qty_value=int(row.quantity)
        price=float(row.price)   
        
        #----- delivery date get from order date
        ym_date=str(delivery_date)[0:7]+'-01'
        req_delivery_date=str(delivery_date)[0:10]
        
        bonus_qty=0
        itemTotal=price*item_qty_value                                
        totalAmount+=itemTotal
        
        short_note=''
        
        #=============== invoice rules check for specific item ; bonus qty no problem, discout+=discount
        if (invoiceRulesFlag==True and anyItemFlag==False and specificItemFlag==True):                                
            for invRow in invRulesRows:
                client_category=str(invRow.client_cat).strip()
                dateFrom=invRow.from_date
                dateTo=invRow.to_date
                itemFor=str(invRow.for_any_item).strip().upper()
                limitFrom=invRow.from_amt_qty
                limitTo=invRow.to_amt_qty
                bonusType=invRow.bonus_type
                                
                b_item_id1=str(invRow.b_item_id1).strip().upper()
                b_item_id2=str(invRow.b_item_id2).strip().upper()
                b_item_id3=str(invRow.b_item_id3).strip().upper()
                
                b_item_qty1=invRow.b_item_qty1
                b_item_qty2=invRow.b_item_qty2
                b_item_qty3=invRow.b_item_qty3
                
                bonus_disc_qty_amt_per=float(invRow.disc_amt_per)
                
                #--------- bonus qty for per(from==to)limited  qty; discAmt and discPer not allowed
                if  ((client_category=='ALL' or client_category==clientCategory) and (orderDate>=dateFrom and orderDate<=dateTo) and itemFor==item_id and limitFrom==limitTo):
                    if (bonusType=='Item'):
                        
                        #======== bonus Item 1
                        if not (b_item_id1=='' or b_item_id1==None):
                            if (item_id==b_item_id1):
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonus_qty=qtySlap*int(b_item_qty1)
                                short_note='bonus %s'%(bonus_qty)
                                
                            else:
                                itemId=''
                                itemName=''
                                categoryId=''
                                itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id1)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                if itemRows:
                                    itemId=itemRows[0].item_id
                                    itemName=itemRows[0].name
                                    categoryId=itemRows[0].category_id
                                
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonusQty=qtySlap*int(b_item_qty1)
                                
                                short_note='bonus item %s (%s)'%(itemId,bonusQty)   # used main item
                                shortNote='bonus for %s'%(item_id)                  # used bonus new item
                                #------------
                                if bonusQty!=0:
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                   'area_id':area_id,'area_name':area_name,'status':'Submitted','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                    detailList.append(detailDict)                                            
                    
                        #======== bonus Item 2
                        if not (b_item_id2=='' or b_item_id2==None):
                            if (item_id==b_item_id2):
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonus_qty=qtySlap*int(b_item_qty2)
                                short_note='bonus %s'%(bonus_qty)
                                
                            else:
                                itemId=''
                                itemName=''
                                categoryId=''
                                itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id2)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                if itemRows:
                                    itemId=itemRows[0].item_id
                                    itemName=itemRows[0].name
                                    categoryId=itemRows[0].category_id
                                
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonusQty=qtySlap*int(b_item_qty2)
                                
                                short_note='bonus item %s (%s)'%(itemId,bonusQty)   # used main item
                                shortNote='bonus for %s'%(item_id)                  # used bonus new item
                                #------------
                                if bonusQty!=0:
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                   'area_id':area_id,'area_name':area_name,'status':'Submitted','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                    detailList.append(detailDict)
                        
                        #======== bonus Item 3
                        if not (b_item_id3=='' or b_item_id3==None):
                            if (item_id==b_item_id3):
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonus_qty=qtySlap*int(b_item_qty3)
                                short_note='bonus %s'%(bonus_qty)
                                
                            else:
                                itemId=''
                                itemName=''
                                categoryId=''
                                itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id3)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                if itemRows:
                                    itemId=itemRows[0].item_id
                                    itemName=itemRows[0].name
                                    categoryId=itemRows[0].category_id
                                
                                qtySlap=int(item_qty_value)/int(limitFrom)
                                qtySlap=int(qtySlap)
                                bonusQty=qtySlap*int(b_item_qty3)
                                
                                short_note='bonus item %s (%s)'%(itemId,bonusQty)   # used main item
                                shortNote='bonus for %s'%(item_id)                  # used bonus new item
                                #------------
                                if bonusQty!=0:
                                    detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                   'area_id':area_id,'area_name':area_name,'status':'Submitted','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                    detailList.append(detailDict)
                        break
                        
                #---------------within range. discount percent,discout amt,bonus qty
                else:
                    if ((client_category=='ALL' or client_category==clientCategory) and (orderDate>=dateFrom and orderDate<=dateTo) and itemFor==item_id and (item_qty_value>=limitFrom and item_qty_value<=limitTo)): 
                        if bonusType=='DiscPer':
                            disAmt=(itemTotal*bonus_disc_qty_amt_per)/100
                            discount+=disAmt
                            short_note='discount %s'%(round(float(disAmt),2))
                            break                                          
                        elif bonusType=='DiscAmt':
                            disAmt=bonus_disc_qty_amt_per
                            discount+=disAmt
                            short_note='discount %s'%(round(float(disAmt),2))
                            break
                        elif bonusType=='Item':
                            #======== bonus Item 1
                            if not (b_item_id1=='' or b_item_id1==None):
                                if (item_id==b_item_id1):
                                    bonus_qty=int(b_item_qty1)
                                    short_note='bonus %s'%(bonus_qty)                                    
                                else:
                                    itemId=''
                                    itemName=''
                                    categoryId=''
                                    itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id1)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                    if itemRows:
                                        itemId=itemRows[0].item_id
                                        itemName=itemRows[0].name
                                        categoryId=itemRows[0].category_id
                                    
                                    bonusQty=int(b_item_qty1)
                                    
                                    short_note='bonus item %s (%s)'%(itemId,bonusQty)  # used main item
                                    shortNote='bonus for %s'%(item_id)                 # used bonus new item
                                    #------------
                                    if bonusQty!=0:
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                       'area_id':area_id,'area_name':area_name,'status':'Submitted','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                        detailList.append(detailDict)                                            
                            
                            #======== bonus Item 2
                            if not (b_item_id2=='' or b_item_id2==None):
                                if (item_id==b_item_id2):
                                    bonus_qty=int(b_item_qty2)
                                    short_note='bonus %s'%(bonus_qty)                                    
                                else:
                                    itemId=''
                                    itemName=''
                                    categoryId=''
                                    itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id2)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                    if itemRows:
                                        itemId=itemRows[0].item_id
                                        itemName=itemRows[0].name
                                        categoryId=itemRows[0].category_id
                                    
                                    bonusQty=int(b_item_qty2)
                                    
                                    short_note='bonus item %s (%s)'%(itemId,bonusQty)  # used main item
                                    shortNote='bonus for %s'%(item_id)                 # used bonus new item
                                    #------------
                                    if bonusQty!=0:
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                       'area_id':area_id,'area_name':area_name,'status':'Submitted','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                        detailList.append(detailDict)                                            
                            
                            #======== bonus Item 3
                            if not (b_item_id3=='' or b_item_id3==None):
                                if (item_id==b_item_id3):
                                    bonus_qty=int(b_item_qty3)
                                    short_note='bonus %s'%(bonus_qty)                                    
                                else:
                                    itemId=''
                                    itemName=''
                                    categoryId=''
                                    itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id3)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                                    if itemRows:
                                        itemId=itemRows[0].item_id
                                        itemName=itemRows[0].name
                                        categoryId=itemRows[0].category_id
                                    
                                    bonusQty=int(b_item_qty3)
                                    
                                    short_note='bonus item %s (%s)'%(itemId,bonusQty)  # used main item
                                    shortNote='bonus for %s'%(item_id)                 # used bonus new item
                                    #------------
                                    if bonusQty!=0:
                                        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                                       'area_id':area_id,'area_name':area_name,'status':'Submitted','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                                        detailList.append(detailDict)                                            
                            break
                        
        #------ get current stock balance for a specific item
        #       totalReqQty=item_qty_value+bonus_qty        
        # here will be checked restricted stock item        
        # here will be checked negative stock allowed or not
        
        #------------
        detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                       'area_id':area_id,'area_name':area_name,'status':'Submitted','item_id':item_id,'item_name':item_name,'category_id':category_id,'quantity':item_qty_value,'bonus_qty':bonus_qty,'price':price,'ym_date':ym_date,'short_note':short_note}
        detailList.append(detailDict)
        if headFlag==False:
            headDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                       'area_id':area_id,'area_name':area_name,'status':'Submitted','ym_date':ym_date}
            headList.append(headDict)
            headFlag=True
            
    #end one order details loop
    orderRecords=''
    
    #=================invoice rules for total amount
    if (invoiceRulesFlag==True and anyItemFlag==True and specificItemFlag==False):                                
        for invRow in invRulesRows:
            client_category=str(invRow.client_cat).strip()
            dateFrom=invRow.from_date
            dateTo=invRow.to_date
            itemFor=str(invRow.for_any_item).strip().upper()
            limitFrom=invRow.from_amt_qty
            limitTo=invRow.to_amt_qty
            bonusType=invRow.bonus_type
            
            b_item_id1=str(invRow.b_item_id1).strip().upper()
            b_item_id2=str(invRow.b_item_id2).strip().upper()
            b_item_id3=str(invRow.b_item_id3).strip().upper()
            
            b_item_qty1=invRow.b_item_qty1
            b_item_qty2=invRow.b_item_qty2
            b_item_qty3=invRow.b_item_qty3
            
            bonus_disc_qty_amt_per=float(invRow.disc_amt_per)                                   
            if ((client_category=='ALL' or client_category==clientCategory) and (orderDate>=dateFrom and orderDate<=dateTo) and itemFor=='ANY' and (totalAmount>=limitFrom and totalAmount<=limitTo)): 
                if bonusType=='DiscPer':
                    discount=(totalAmount*bonus_disc_qty_amt_per)/100
                    break                                          
                elif bonusType=='DiscAmt':
                    discount=bonus_disc_qty_amt_per
                    break
                elif bonusType=='Item':
                    #======== bonus Item 1
                    if not (b_item_id1=='' or b_item_id1==None):                        
                        itemId=''
                        itemName=''
                        categoryId=''
                        itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id1)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                        if itemRows:
                            itemId=itemRows[0].item_id
                            itemName=itemRows[0].name
                            categoryId=itemRows[0].category_id
                        
                        bonusQty=b_item_qty1
                        shortNote='bonus for total amount'
                        #------------
                        if bonusQty!=0:
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                           'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                            detailList.append(detailDict)                                            
                    
                    #======== bonus Item 2
                    if not (b_item_id2=='' or b_item_id2==None):                        
                        itemId=''
                        itemName=''
                        categoryId=''
                        itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id2)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                        if itemRows:
                            itemId=itemRows[0].item_id
                            itemName=itemRows[0].name
                            categoryId=itemRows[0].category_id
                        
                        bonusQty=b_item_qty2
                        shortNote='bonus for total amount'
                        #------------
                        if bonusQty!=0:
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                           'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                            detailList.append(detailDict)
                    
                    #======== bonus Item 3
                    if not (b_item_id3=='' or b_item_id3==None):                        
                        itemId=''
                        itemName=''
                        categoryId=''
                        itemRows=db((db.sm_item.cid==c_id) & (db.sm_item.item_id==b_item_id3)).select(db.sm_item.item_id,db.sm_item.name,db.sm_item.category_id,limitby=(0,1))
                        if itemRows:
                            itemId=itemRows[0].item_id
                            itemName=itemRows[0].name
                            categoryId=itemRows[0].category_id
                        
                        bonusQty=b_item_qty3
                        shortNote='bonus for total amount'
                        #------------
                        if bonusQty!=0:
                            detailDict={'cid':c_id,'depot_id':depot_id,'depot_name':depot_name,'sl':maxSl,'order_sl':sl,'client_id':client_id,'client_name':client_name,'rep_id':rep_id,'rep_name':rep_name,'order_datetime':order_datetime,'delivery_date':req_delivery_date,'payment_mode':payment_mode,'note':req_note,
                                           'area_id':area_id,'area_name':area_name,'status':'Invoiced','item_id':itemId,'item_name':itemName,'category_id':categoryId,'quantity':0,'bonus_qty':bonusQty,'price':0,'ym_date':ym_date,'short_note':shortNote}
                            detailList.append(detailDict)
                    break
                    
                    
    #-----------------
    
    discount=round(float(discount),2)
    totalAmount=totalAmount-discount                    
    
    retMsg=''
    #=============== Insert invoice head and details
    if (len(headList)> 0 and len(detailList) > 0):
        #---------- dicount amount assigned
        for i in range(len(headList)):
            headDictData=headList[i]
            headDictData['discount']=discount
            
        for j in range(len(detailList)):
            detailDictData=detailList[j]
            detailDictData['discount']=discount
        
        #------------- call balance update function
#        strData=str(c_id)+'<fdfd>DELIVERY<fdfd>'+str(maxSl)+'<fdfd>'+str(datetime_fixed)+'<fdfd>'+str(depot_id)+'-'+str(maxSl)+'<fdfd>DPT-'+str(depot_id)+'<fdfd>CLT-'+str(client_id)+'<fdfd>'+str(totalAmount)
#        resStr=set_balance_transaction(strData)        
#        resStrList=resStr.split('<sep>',resStr.count('<sep>'))
#        flag=resStrList[0]
#        msg=resStrList[1]
#        if flag=='True':
        
        #Update status of head and detail                
        rows=db.sm_invoice.bulk_insert(detailList)
        rows=db.sm_invoice_head.bulk_insert(headList)                        
        db((db.sm_order_head.cid==c_id) & (db.sm_order_head.depot_id==depot_id) & (db.sm_order_head.client_id==client_id)&(db.sm_order_head.sl==sl)).update(status='Invoiced',invoice_ref=maxSl,flag_data='1')#delivery_date=req_delivery_date,
        db((db.sm_order.cid==c_id) & (db.sm_order.depot_id==depot_id) & (db.sm_order.client_id==client_id)&(db.sm_order.sl==sl)).update(status='Invoiced',invoice_ref=maxSl)#delivery_date=req_delivery_date,
        retMsg='Successfully Imported'
        db.commit()
        
    #-------------- end order
    invRulesRows=''
    
    return retMsg+','+str(maxSl)
    
#type=ISSUE,RECEIVE,DAMAGE,DELIVERY,RETURN
def update_depot_stock(type,cid,depotid,sl):
    updateType=type
    c_id=cid
    depot_id=depotid
    depot_sl=sl
    
    if updateType=='ISSUE':
        issueRow=db((db.sm_issue.cid==c_id)& (db.sm_issue.depot_id==depot_id) & (db.sm_issue.sl==depot_sl) & (db.sm_issue.status=='Posted')& (db.sm_issue.flag_depot_stock_balance==0)).select(db.sm_issue.store_id,limitby=(0,1))
        if issueRow:
            store_id=issueRow[0].store_id
            
            updateRecords="update sm_depot_stock_balance dsb,sm_issue iss  set dsb.quantity=(dsb.quantity-(iss.quantity+iss.bonus_qty)) where (iss.cid='"+str(c_id)+"' and iss.depot_id='"+str(depot_id)+"' and iss.sl="+str(depot_sl)+" and iss.store_id='"+str(store_id)+"' and dsb.cid='"+str(c_id)+"' and dsb.depot_id='"+str(depot_id)+"' and dsb.store_id='"+str(store_id)+"' and iss.item_id=dsb.item_id and iss.batch_id=dsb.batch_id)"
            db.executesql(updateRecords)
            
            # effect in details not to used head flag
            db((db.sm_issue.cid==c_id)& (db.sm_issue.depot_id==depot_id) & (db.sm_issue.sl==depot_sl)).update(flag_depot_stock_balance=1)
            
    elif updateType=='RECEIVE':
        receiveRow=db((db.sm_receive.cid==c_id)& (db.sm_receive.depot_id==depot_id) & (db.sm_receive.sl==depot_sl) & (db.sm_receive.status=='Posted')&(db.sm_receive.flag_depot_stock_balance==0)).select(db.sm_receive.store_id,limitby=(0,1))
        if receiveRow:
            store_id=receiveRow[0].store_id
            
            updateRecords="update sm_depot_stock_balance dsb,sm_receive rec  set dsb.quantity=(dsb.quantity+(rec.quantity+rec.bonus_qty)) where (rec.cid='"+str(c_id)+"' and rec.depot_id='"+str(depot_id)+"' and rec.sl="+str(depot_sl)+" and rec.store_id='"+str(store_id)+"' and dsb.cid='"+str(c_id)+"' and dsb.depot_id='"+str(depot_id)+"' and dsb.store_id='"+str(store_id)+"' and rec.item_id=dsb.item_id and rec.batch_id=dsb.batch_id)"
            db.executesql(updateRecords)
            
            # effect in details not to used head flag
            db((db.sm_receive.cid==c_id)& (db.sm_receive.depot_id==depot_id) & (db.sm_receive.sl==depot_sl)).update(flag_depot_stock_balance=1)
            
    elif updateType=='TRANSFER':
        damageRow=db((db.sm_damage.cid==c_id)& (db.sm_damage.depot_id==depot_id) & (db.sm_damage.sl==depot_sl) & (db.sm_damage.status=='Posted')&(db.sm_damage.flag_depot_stock_balance==0)).select(db.sm_damage.store_id,db.sm_damage.store_id_to,db.sm_damage.adjustment_type,limitby=(0,1))
        if damageRow:
            store_id=damageRow[0].store_id
            store_id_to=damageRow[0].store_id_to
            
            #from store
            fromRecords="update sm_depot_stock_balance dsb,sm_damage dam  set dsb.quantity=(dsb.quantity-dam.quantity) where (dam.cid='"+str(c_id)+"' and dam.depot_id='"+str(depot_id)+"' and dam.sl="+str(depot_sl)+" and dam.store_id='"+str(store_id)+"' and dsb.cid='"+str(c_id)+"' and dsb.depot_id='"+str(depot_id)+"' and dsb.store_id='"+str(store_id)+"' and dam.item_id=dsb.item_id and dam.batch_id=dsb.batch_id)"
            db.executesql(fromRecords)
            
            #To store
            if store_id_to!='':
                toRecords="update sm_depot_stock_balance dsb,sm_damage dam  set dsb.quantity=(dsb.quantity+dam.quantity) where (dam.cid='"+str(c_id)+"' and dam.depot_id='"+str(depot_id)+"' and dam.sl="+str(depot_sl)+" and dam.store_id_to='"+str(store_id_to)+"' and dsb.cid='"+str(c_id)+"' and dsb.depot_id='"+str(depot_id)+"' and dsb.store_id='"+str(store_id_to)+"' and dam.item_id=dsb.item_id and dam.batch_id=dsb.batch_id)"
                db.executesql(toRecords)
            
            # effect in details not to used head flag
            db((db.sm_damage.cid==c_id)& (db.sm_damage.depot_id==depot_id) & (db.sm_damage.sl==depot_sl)).update(flag_depot_stock_balance=1)
            
    elif updateType=='DAMAGE':
        damageRow=db((db.sm_damage.cid==c_id)& (db.sm_damage.depot_id==depot_id) & (db.sm_damage.sl==depot_sl) & (db.sm_damage.status=='Posted')&(db.sm_damage.flag_depot_stock_balance==0)).select(db.sm_damage.store_id,db.sm_damage.adjustment_type,limitby=(0,1))
        if damageRow:
            store_id=damageRow[0].store_id
            adjustment_type=damageRow[0].adjustment_type
            
            if adjustment_type=='Decrease':
                updateRecords="update sm_depot_stock_balance dsb,sm_damage dam  set dsb.quantity=(dsb.quantity-dam.quantity) where (dam.cid='"+str(c_id)+"' and dam.depot_id='"+str(depot_id)+"' and dam.sl="+str(depot_sl)+" and dam.store_id='"+str(store_id)+"' and dsb.cid='"+str(c_id)+"' and dsb.depot_id='"+str(depot_id)+"' and dsb.store_id='"+str(store_id)+"' and dam.item_id=dsb.item_id and dam.batch_id=dsb.batch_id)"
            elif adjustment_type=='Increase':
                updateRecords="update sm_depot_stock_balance dsb,sm_damage dam  set dsb.quantity=(dsb.quantity+dam.quantity) where (dam.cid='"+str(c_id)+"' and dam.depot_id='"+str(depot_id)+"' and dam.sl="+str(depot_sl)+" and dam.store_id='"+str(store_id)+"' and dsb.cid='"+str(c_id)+"' and dsb.depot_id='"+str(depot_id)+"' and dsb.store_id='"+str(store_id)+"' and dam.item_id=dsb.item_id and dam.batch_id=dsb.batch_id)"
                
            db.executesql(updateRecords)
            
            # effect in details not to used head flag
            db((db.sm_damage.cid==c_id)& (db.sm_damage.depot_id==depot_id) & (db.sm_damage.sl==depot_sl)).update(flag_depot_stock_balance=1)
    
    
    elif updateType=='DELIVERY':
        delRow=db((db.sm_invoice.cid==c_id)& (db.sm_invoice.depot_id==depot_id) & (db.sm_invoice.sl==depot_sl) & (db.sm_invoice.status=='Invoiced')& (db.sm_invoice.flag_depot_stock_balance==0)).select(db.sm_invoice.store_id,limitby=(0,1))
        if delRow:
            store_id=delRow[0].store_id
            
            #updateRecords="update sm_depot_stock_balance dsb,sm_invoice inv  set dsb.quantity=(dsb.quantity-(inv.quantity+inv.bonus_qty)) where (inv.cid='"+str(c_id)+"' and inv.depot_id='"+str(depot_id)+"' and inv.sl="+str(depot_sl)+" and inv.store_id='"+str(store_id)+"' and dsb.cid='"+str(c_id)+"' and dsb.depot_id='"+str(depot_id)+"' and dsb.store_id='"+str(store_id)+"' and inv.item_id=dsb.item_id and inv.batch_id=dsb.batch_id)"
            
            updateRecords="update sm_depot_stock_balance dsb,(select invtemp.cid as cid,invtemp.depot_id as depot_id,invtemp.sl as sl,invtemp.store_id as store_id,invtemp.item_id as item_id,invtemp.batch_id as batch_id,sum(invtemp.quantity) as quantity,sum(invtemp.bonus_qty) as bonus_qty from sm_invoice invtemp where (invtemp.cid='"+str(c_id)+"' and invtemp.depot_id='"+str(depot_id)+"' and invtemp.sl="+str(depot_sl)+" and invtemp.store_id='"+str(store_id)+"') group by invtemp.cid,invtemp.depot_id,invtemp.sl,invtemp.store_id,invtemp.item_id,invtemp.batch_id) inv  set dsb.quantity=(dsb.quantity-(inv.quantity+inv.bonus_qty)),dsb.block_qty=(dsb.block_qty-(inv.quantity+inv.bonus_qty)) where (inv.cid='"+str(c_id)+"' and inv.depot_id='"+str(depot_id)+"' and inv.sl="+str(depot_sl)+" and inv.store_id='"+str(store_id)+"' and dsb.cid='"+str(c_id)+"' and dsb.depot_id='"+str(depot_id)+"' and dsb.store_id='"+str(store_id)+"' and inv.item_id=dsb.item_id and inv.batch_id=dsb.batch_id)"
            db.executesql(updateRecords)
            
            #-----------------            
            # effect in details not to used head flag
            db((db.sm_invoice.cid==c_id)& (db.sm_invoice.depot_id==depot_id) & (db.sm_invoice.sl==depot_sl)).update(flag_depot_stock_balance=1)
    
    return 'Done'

def x_handel_upto_99(number):
    predef={0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",19:"nineteen",20:"twenty",30:"thirty",40:"fourty",50:"fifty",60:"sixty",70:"seventy",80:"eighty",90:"ninety",100:"hundred",100000:"lakh",10000000:"crore",1000000:"million",1000000000:"billion"}
    if number in predef.keys():
        return predef[number]
    else:
        return predef[(number/10)*10]+' '+predef[number%10]
        
def x_return_bigdigit(number,devideby):
    predef={0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",19:"nineteen",20:"twenty",30:"thirty",40:"fourty",50:"fifty",60:"sixty",70:"seventy",80:"eighty",90:"ninety",100:"hundred",1000:"thousand",100000:"lakh",10000000:"crore",1000000:"million",1000000000:"billion"}
    if devideby in predef.keys():
        return predef[number/devideby]+" "+predef[devideby]
    else:
        devideby/=10
        return handel_upto_99(number/devideby)+" "+predef[devideby]
        
#================================= Number To word conversion
def handel_upto_99(number):
    predef={0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",19:"nineteen",20:"twenty",30:"thirty",40:"forty",50:"fifty",60:"sixty",70:"seventy",80:"eighty",90:"ninety",100:"hundred",100000:"lakh",10000000:"crore"}
    if number in predef.keys():
        return predef[number]
    else:
        return predef[(number/10)*10]+' '+predef[number%10]

def return_bigdigit(number,devideby):
    predef={0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",19:"nineteen",20:"twenty",30:"thirty",40:"forty",50:"fifty",60:"sixty",70:"seventy",80:"eighty",90:"ninety",100:"hundred",1000:"thousand",100000:"lakh",10000000:"crore"}
    if devideby in predef.keys():
        return predef[number/devideby]+" "+predef[devideby]
    else:
        devideby/=10
        return handel_upto_99(number/devideby)+" "+predef[devideby]


def mainfunction(number):
    dev = {100: "hundred", 1000: "thousand", 100000: "lakh", 10000000: "crore"}
    if number is 0:
        return "Zero"
    if number < 100:
        result = handel_upto_99(number)

    else:
        result = ""
        while number >= 100:
            devideby = 1
            length = len(str(number))

            for i in range(length - 1):
                devideby *= 10

            #            if number%devideby==0:
            #                if devideby in dev:
            #                    return handel_upto_99(number/devideby)+" "+ dev[devideby]
            #                else:
            #                    return handel_upto_99(number/(devideby/10))+" "+ dev[devideby/10]

            res = return_bigdigit(number, devideby)
            result = result + ' ' + res

            if devideby not in dev:
                number = number - ((devideby / 10) * (number / (devideby / 10)))

            number = number - devideby * (number / devideby)

        if 0 < number < 100:
            result = result + ' ' + handel_upto_99(number)

    return result

def num2word(num_amount):
    temp_amount=str(num_amount)

    if '.' in temp_amount:
        amount = temp_amount.split('.')
        taka = amount[0]
        paisa = amount[1]
    else:
        taka = temp_amount
        paisa = '0'

    # from num2words import num2words

    # Most common usage.
    # amtWord=mainfunction(num2words(taka))

    # amtWord = mainfunction(long(taka))
    # amtWord= mainfunction(bigint(taka))
    paisaWord = mainfunction(int(paisa))

    # if paisaWord=='Zero':
    #     total = 'Taka '+ str(amtWord)+ ' only'
    # else:
    #     total = 'Taka '+ str(amtWord) + ' and paisa '+ str(paisaWord)+ ' only'

    if paisaWord=='Zero':
        total = 'Taka '+ str(taka)+ ' only'
    else:
        total = 'Taka '+ str(taka) + ' and paisa '+ str(paisa)+ ' only'
    return total

#=================== two digit after decimal point
def easy_format(amount,temp):
    return '{0:.2f}'.format(amount)

def easy_format(num):    
    return '{0:20,.2f}'.format(num)
    
#=======================Set Product List for mobile app
#Call this function from Item process
def set_product_list(cid):
    productStr = ''
    productRows = db(db.sm_item.cid == cid).select(db.sm_item.item_id, db.sm_item.name, db.sm_item.price,db.sm_item.vat_amt, orderby=db.sm_item.name)
    for productRow in productRows:
        item_id = productRow.item_id
        name = productRow.name
        price = productRow.price
        vat_amt = productRow.vat_amt
        
        salesPrice=0
        try:
            salesPrice=round(price+vat_amt,2)
        except:
            salesPrice=0
        
        if productStr == '':
            productStr = str(item_id) + '<fd>' + str(name) + '<fd>' + str(salesPrice)
        else:
            productStr += '<rd>' + str(item_id) + '<fd>' + str(name) + '<fd>' + str(salesPrice)
    
    db(db.sm_company_settings.cid==cid).update(item_list_mobile=productStr)
    
    return 'Done'


#===


# =========================
def check_special_char_address(strData):
    strData=strData.replace("`", "")
    strData=strData.replace("@", "")
    strData=strData.replace("#", "")#p
    strData=strData.replace("$", "")#p
    strData=strData.replace("%", "")
    strData=strData.replace("^", "")
    strData=strData.replace("&", "")#p
    strData=strData.replace("*", "")
    strData=strData.replace("<", "")
    strData=strData.replace(">", "")
    strData=strData.replace("(", "")
    strData=strData.replace(")", "")
    strData=strData.replace("+", "")
    strData=strData.replace("=", "")
    strData=strData.replace("\"", "")
    strData=strData.replace("\'", "")
    strData=strData.replace("{", "")
    strData=strData.replace("}", "")
    strData=strData.replace("[", "")
    strData=strData.replace("]", "")
    strData=strData.replace(",", "")
    strData=strData.replace("'", "")
    strData=strData.replace('"', '')
    strData=strData.replace(";", "")   
    strData=strData.replace(".", "")
    strData=strData.replace("!", "")
    return strData
