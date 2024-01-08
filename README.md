# 台北一日遊
> 台北一日遊是一個電商網站專案，採用前後端分離設計。  
> 展示網址：http://52.64.119.167:3000/
> + 前端：HTML, SCSS, JavaScript
> + 後端：Python Flask 

## 特點
+ RESTful API  
  > /api
  >> /user
  >>> /auth 
  > 
  >> /attractions
  >>> /\<attractionID\>
  > 
  >> /mrts
  > 
  >> /booking
  >  
  >> /orders
  >>> /\<orderNumber\>
+ 資料庫
  > MySQL
  ![](https://github.com/jimhop19/wehelp_phase2/blob/main/demo%20picture/database%20schema.png)

## 功能
+ 會員系統
  > 測試帳號：test@gmail.com
  > 測試密碼：test
+ 結帳系統
  > 串接TapPay
  > 測試卡號：
    + 卡號：4242 4242 4242 4242
    + CCV：123
    + 卡片效期：使用超過目前年月份的效期即可
+ 商品頁面  
  * 響應式設計
    ![](https://github.com/jimhop19/wehelp_phase2/blob/main/demo%20picture/RWD%20Website)   
  * 延遲載入
    ![](https://github.com/jimhop19/wehelp_phase2/blob/main/demo%20picture/lazy%20loading%20s.gif)
