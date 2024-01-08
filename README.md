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
+ 商品頁面  
  * 響應式設計  
  * 延遲載入
    <iframe width="560" height="315" src="https://www.youtube.com/embed/-vHoBTdZ6cQ?si=elT9RX1ht6DNvdat" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
+ 會員系統
+ 結帳系統
  > 串接TapPay
