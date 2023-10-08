from flask import *
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
import re
import jwt
key = "secret"
from datetime import datetime,timezone,timedelta
import requests
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
partner_key = os.getenv("partner_key")

dbconfg = {
	"host" : "127.0.0.1",
	"username" : "root",
	"password" : "12345678",
	"db" : "attraction_database",

}
mydb = mysql.connector.pooling.MySQLConnectionPool(
	pool_name="attraction",
	pool_size= 32,		
	**dbconfg
)

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():		
	return render_template("booking.html")	
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

@app.route("/api/user",methods=["POST"])
def signUp():
	signUpData = json.loads(request.data)	
	name = signUpData["name"]
	email = signUpData["email"]
	password = signUpData["password"]
	signUpRegex = "^\w+$"
	emailRegex = "^\w+@\w+\.\w+$"
	mydbConnection = mydb.get_connection()
	cursor = mydbConnection.cursor()
	cursor.execute("SELECT email FROM member WHERE email = %(email)s",{"email":email})
	alreadyInUseEmail = cursor.fetchall()
	mydbConnection.close()	
	if re.search(signUpRegex,name) == None or re.search(emailRegex,email) == None or re.search(signUpRegex,password) == None:		
		return{"error":True,"message":"不得含有特殊字元"}
	elif alreadyInUseEmail != []:		
		return{"error":True,"message":"此電子信箱已經註冊過"}
	else:
		mydbConnection = mydb.get_connection()
		cursor = mydbConnection.cursor()
		cursor.execute("INSERT INTO member (name,email,password) VALUE(%s,%s,%s)",(name,signUpData["email"],signUpData["password"]))
		mydbConnection.commit()
		mydbConnection.close()		
		return {"ok":True}	
@app.route("/api/user/auth",methods=["GET","PUT"])
def signIn():	
	#check sign in status
	if request.method == "GET":		
		try:				
			string = request.headers["Authorization"]
			token = string[7:]
			dataFromToken = jwt.decode(token, key, algorithms="HS256")			
			return{"data":{"id":dataFromToken["id"],"name":dataFromToken["name"],"email":dataFromToken["email"]}}
		except jwt.ExpiredSignatureError:
			return {"data" : None}
	#signin		
	elif request.method == "PUT":
		signInData = json.loads(request.data)	
		email = signInData["email"]		
		password = signInData["password"]
		signUpRegex = "^\w+$"
		emailRegex = "^\w+@\w+\.\w+$"
		if re.search(emailRegex,email) == None or re.search(signUpRegex,password) == None:
			return {"error":True,"message":"帳號或密碼格式錯誤"}
		mydbConnection = mydb.get_connection()
		cursor = mydbConnection.cursor()
		cursor.execute("SELECT password,id,name,email FROM member WHERE email = %(email)s",{"email":email})
		checkResult = cursor.fetchall()		
		
		if checkResult != []:
			passwordFromDatabase = checkResult[0][0]					
			if password == passwordFromDatabase:				
				jwt_payload ={"exp": datetime.now(tz=timezone.utc) + timedelta(days=7),"id":checkResult[0][1],"name":checkResult[0][2],"email":checkResult[0][3]}
				encodedToken = jwt.encode(jwt_payload, key, algorithm="HS256")
				cursor.execute("UPDATE member SET token = %(token)s WHERE email = %(email)s",{"token":encodedToken,"email":email})
				mydbConnection.commit()
				mydbConnection.close()
				return {"token":encodedToken}
			else:
				mydbConnection.close()
				return {"error":True,"message":"密碼錯誤"}
		else:
			mydbConnection.close()
			return{"error":True,"message":"此e-mail尚未註冊"}


@app.route("/api/attractions", methods=["GET"])
def attractionsList():		
	intRegex = "^\d*$"
	pageFromQueryString = request.args.get("page")	
	keywordRegex = "^\w*$"
	keywordFromQueryString = request.args.get("keyword")
	#check if Query String is correct format
	if re.search(intRegex,pageFromQueryString) == None:
		return {"error":True,"message":"Page number should be interger"}
	elif keywordFromQueryString != None and re.search(keywordRegex,keywordFromQueryString) == None:
		return {"error":True,"message":"Please do not enter special characters"}
	
	#search in database
	mydbConnection = mydb.get_connection()	
	cursor = mydbConnection.cursor()
	if keywordFromQueryString != None:
		cursor.execute("SELECT * FROM attraction WHERE name LIKE %(keywordPlus)s OR mrt = %(keyword)s LIMIT %(page)s,12",{"keywordPlus":"%"+keywordFromQueryString+"%","keyword":keywordFromQueryString,"page":int(pageFromQueryString)*12})
	else:
		cursor.execute("SELECT * FROM attraction LIMIT %(page)s,12",{"page":int(pageFromQueryString)*12})
	attractionsList = cursor.fetchall()
	mydbConnection.close()	

	result = {}
	result["data"] = []
	for x in attractionsList:		
		result["data"].append(createAttractionData(x))
	#next page
	if len(result["data"]) <12:
		result["nextPage"] = None
	else:
		result["nextPage"] = int(pageFromQueryString)+1

	return json.dumps(result,ensure_ascii = False)
	
def createAttractionData(source):
	data = {}
	data["id"] = source[0]
	data["name"] = source[1]
	data["category"] = source[2]
	data["description"] = source[3]
	data["address"] = source[4]
	data["transport"] = source[5]
	data["mrt"] = source[6]
	data["lat"] = source[7]
	data["lng"] = source[8]
	data["images"] = splitJPGURL(source[9])
	return data	
def splitJPGURL(string):
		regex = "http.*?\.jpg"
		jpgFile = re.findall(regex,string,re.IGNORECASE)
		return jpgFile

@app.route("/api/attraction/<int:attractionID>", methods=["GET"])
def attraction_byID(attractionID):
	if attractionID < 0:
		return {"error":True,"message":"attractionId should be positive integer"}
	else:
		mydbConnection = mydb.get_connection()
		cursor = mydbConnection.cursor()
		cursor.execute("SELECT * FROM attraction WHERE id = %(ID)s",{"ID":attractionID})
		dataFromDatabase = cursor.fetchall()
		mydbConnection.close()	
		
		if dataFromDatabase == []:
			return{"error":True,"message":"attractionID is incorrect"}
		else:			
			result = {}
			result["data"] = createAttractionData(dataFromDatabase[0])
			return json.dumps(result,ensure_ascii = False)		
		
@app.route("/api/mrts",methods=["GET"])
def mrts():
	mydbConnection = mydb.get_connection()
	cursor = mydbConnection.cursor()
	cursor.execute("SELECT mrt FROM attraction")
	dataFromDatabase = cursor.fetchall()
	mydbConnection.close()
	#transfer data to a list
	dataOriginal = []
	for x in dataFromDatabase:
		dataOriginal.append(x[0])
	#count which mrt station occurred the most
	import collections
	mrtCount = collections.Counter(dataOriginal).most_common()
	#transfer to json and return result
	data = []
	for x in mrtCount:
		if x[0] != None:
			data.append(x[0])
	result = {}
	result["data"] = data
	return json.dumps(result,ensure_ascii = False)

@app.route("/api/booking",methods=["GET","POST","DELETE"])
def bookingSystem():	
	try:
		string = request.headers["Authorization"]
		token = string[7:]
		dataFromToken = jwt.decode(token, key, algorithms="HS256")
		memberID = dataFromToken["id"]
		if request.method == "POST":
			requestData = json.loads(request.data)			
			mydbConnection = mydb.get_connection()
			cursor = mydbConnection.cursor()
			cursor.execute("SELECT id FROM booking WHERE member_id = %(bookingID)s AND payment_status = 1",{"bookingID":memberID})	
			unpaidBookingID = cursor.fetchall()			
			if unpaidBookingID == []:
				cursor.execute("INSERT INTO booking (member_id,payment_status) Value (%s,%s)",(memberID,1))
				mydbConnection.commit()
				cursor.execute("SELECT id FROM booking WHERE member_id = %(bookingID)s AND payment_status = 1",{"bookingID":memberID})	
				newBookingID = cursor.fetchall()[0][0]
				bookingID = newBookingID
			else:
				bookingID = unpaidBookingID[0][0]		
			requestAttractionId = requestData["attractionId"]
			requestDate = requestData["date"]
			requestTime = requestData["time"]
			requestPrice = requestData["price"]				
			cursor.execute("INSERT INTO booking_detail (booking_id,attraction_id,date,time,price) VALUE (%s,%s,%s,%s,%s)",(bookingID,requestAttractionId,requestDate,requestTime,requestPrice))
			mydbConnection.commit()
			mydbConnection.close()
			return {"ok":True}
		if request.method == "GET":
			mydbConnection = mydb.get_connection()
			cursor = mydbConnection.cursor()			
			cursor.execute("SELECT id FROM booking WHERE member_id = %(memberID)s AND payment_status = 1",{"memberID":memberID})
			unpaidBookingID = cursor.fetchall()			
			if unpaidBookingID == []:
				mydbConnection.close()
				return{"data":None}
			else:
				bookingID = unpaidBookingID[0][0]
				cursor.execute("SELECT attraction_id,date,time,price,id FROM booking_detail WHERE booking_id = %(bookingID)s",{"bookingID":bookingID})
				dataFromDatabase = cursor.fetchall()				
				data = []
				if dataFromDatabase == []:
					mydbConnection.close()
					return{"data":data}
				else:
					for x in dataFromDatabase:
						item = {}
						attractionID = x[0]
						cursor.execute("SELECT name,address,images FROM attraction WHERE id = %(attractionID)s",{"attractionID":attractionID})
						attractionData = cursor.fetchall()
						imageRegex = "http.*?\.jpg"
						item["attraction"] = {"id":attractionID,"name":attractionData[0][0],"address":attractionData[0][1],"image":re.findall(imageRegex,attractionData[0][2],re.IGNORECASE)[0]}
						item["date"] = x[1].strftime("%Y-%m-%d")
						item["time"] = x[2]
						item["price"] = x[3]
						item["bookingDetailID"] = x[4]
						data.append(item)				
					mydbConnection.close()			
					return{"data":data}
		if request.method == "DELETE":
			try:
				bookingDetailID = request.data				
				mydbConnection = mydb.get_connection()
				cursor = mydbConnection.cursor()
				cursor.execute("DELETE FROM booking_detail WHERE id = %(bookingDetailID)s",{"bookingDetailID":bookingDetailID})
				mydbConnection.commit()
				mydbConnection.close()
				return {"ok":True}
			except:
				return {"error":True,"message":"Internal Error"}
						
	except jwt.ExpiredSignatureError:
		return {"error":True,"message":"請先登入"}
	except Exception:
		return {"error":True,"message":"Internal error"}
@app.route("/api/orders",methods=["POST"])
def Order():
	try:
		authorizationResult = authorization()		
		if authorizationResult["error"] == True:
			return ("/")
	except:
		data_from_frontend = json.loads(request.data)	
		prime = data_from_frontend["prime"]
		price = data_from_frontend["order"]["price"]
		contact = data_from_frontend["order"]["contact"]
		name = contact["name"]
		email = contact["email"]
		phone_number = contact["phone"]		
		url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
		headers = {
			"Content-Type": "application/json",
			"x-api-key": partner_key
		}
		data = {
			"prime": prime,
			"partner_key": partner_key,
			"merchant_id": "jimhop_NCCC",
			"details": "TapPay Test",
			"amount": price,
			"cardholder": {
				"phone_number": phone_number,
				"name": name,
				"email": email		
			}
		}
		result_from_tappay = requests.post(url,headers=headers,json=data, timeout=30)		
		result = json.loads(f"{result_from_tappay.text}")
		def format_time(input):
			if input < 10 :
				return "0"+f"{input}"
			else:
				return input
		def payment_status(status_number):
			current_datetime = datetime.now(tz=timezone(timedelta(hours=8)))
			order_number = f"{current_datetime.year}"+f"{format_time(current_datetime.month)}"+f"{format_time(current_datetime.day)}"+f"{format_time(current_datetime.hour)}"+f"{format_time(current_datetime.minute)}"+f"{format_time(current_datetime.second)}"
			mydbconnenction = mydb.get_connection()
			cursor = mydbconnenction.cursor()
			cursor.execute("UPDATE booking SET payment_status = %(status_number)s, order_number = %(order_number)s, contact_name = %(contact_name)s, contact_email = %(contact_email)s, contact_phone = %(contact_phone)s,total_price = %(total_price)s WHERE member_id = %(memberID)s AND payment_status = 1;",{"status_number":status_number,"order_number":order_number,"contact_name":name,"contact_email":email,"contact_phone":phone_number,"memberID":authorizationResult["id"],"total_price":price})
			mydbconnenction.commit()
			mydbconnenction.close()
			dataBackToFrontEnd = {"data":{"number":order_number,"payment":{"status":status_number,"message":"付款成功"}}}	
			return json.dumps(dataBackToFrontEnd)
		if result["status"] == 0:
			return payment_status(0)
		else :
			return payment_status(1)

def authorization():
	try:
		string = request.headers["Authorization"]
		token = string[7:]
		dataFromToken = jwt.decode(token, key, algorithms="HS256")
		memberID = dataFromToken["id"]
		memberEmail = dataFromToken["email"]
		memberName = dataFromToken["name"]
		return{"id":memberID,"email":memberEmail,"name":memberName}
	except jwt.ExpiredSignatureError:
		return {"error":True,"message":"請先登入"}
	except Exception:
		return {"error":True,"message":"Internal error"}
@app.route("/api/order/<int:orderNumber>",methods=["GET"])
def searchOrder(orderNumber):
	authorization()	
	mydbconnection = mydb.get_connection()
	cursor = mydbconnection.cursor()
	cursor.execute("SELECT attraction_id,date,time,price,booking.contact_name,booking.contact_email,booking.contact_phone,total_price,payment_status From booking_detail LEFT JOIN booking ON booking_detail.booking_id = booking.id WHERE booking.order_number = %(order_number)s ORDER BY booking_detail.date;",{"order_number":orderNumber})
	result = cursor.fetchall()
	mydbconnection.close()
	print(result)
	if result != []:
		trip = []	
		for x in result:
			item = {}
			attraction = {}
			mydbconnection = mydb.get_connection()
			cursor = mydbconnection.cursor()
			cursor.execute("SELECT name,address,images FROM attraction WHERE id = %(id)s",{"id":x[0]})
			attractionInformation = cursor.fetchall()
			mydbconnection.close()
			attraction["id"] = x[0]
			attraction["name"] = attractionInformation[0][0]
			attraction["address"] = attractionInformation[0][1]
			attraction["image"] = splitJPGURL(attractionInformation[0][2])[0]
			item["attraction"] = attraction
			item["date"] = x[1].strftime("%Y-%m-%d")
			item["time"] = x[2]		
			trip.append(item)
		data = {
			"number": orderNumber,
			"price": result[0][7],
			"trip": trip,
			"contact": {
				"name": result[0][4],
				"email": result[0][5],
				"phone": result[0][6]
			},
			"status": result[0][8]
		}	
		return json.dumps({"data":data})
	else:
		return json.dumps({
			"error": True,
			"message": "no match order number"
		})	


app.run(host="0.0.0.0", port=3000)