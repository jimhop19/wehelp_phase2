from flask import *
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
import re
import mysql.connector
dbconfg = {
	"host" : "127.0.0.1",
	"username" : "root",
	"password" : "12345678",
	"db" : "attraction_database",

}
mydb = mysql.connector.pooling.MySQLConnectionPool(
	pool_name="attraction",
	pool_size= 10,		
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
	import jwt
	key = "secret"
	from datetime import datetime,timezone,timedelta
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

app.run(host="0.0.0.0", port=3000)