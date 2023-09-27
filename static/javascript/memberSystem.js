const signInAndSignUp = document.getElementById("signInAndSignUp");
const memberPage = document.querySelector(".darkenBackground");
const signOutButton = document.getElementById("signOut");
//open memberpage     
signInAndSignUp.addEventListener("click",() => {
    switchToSignIn();
    memberPage.style.display = "block";
    const signInEmailInput = document.getElementById("signInEmailInput");
    signInEmailInput.focus();
});
//close memberpage
const closeMemberPage = document.getElementById("closePage");
closeMemberPage.addEventListener("click",() => {
    memberPage.style.display = "none"
});
memberPage.addEventListener("click",(event)=>{       
    if(event.target != memberPage){        
        return;
    }else if(memberPage.style.display == "block"){        
        memberPage.style.display = "none"
    }     
});
//autofocus
const signInPasswordInput = document.getElementById("signInPasswordInput");
signInPasswordInput.addEventListener("keypress",function(event){
    if (event.key === "Enter"){
        signIn()
    }
});
const signUpPasswordInput = document.getElementById("signUpPassword");
signUpPasswordInput.addEventListener("keypress",function(event){
    if (event.key === "Enter"){
        signUp()
    }
});
//check sign in status
window.onload = checkSignInStatus();    
function signIn(){
    const email = document.getElementById("signInEmailInput").value
    const password = document.getElementById("signInPasswordInput").value
    const signInSuccessMessage = document.getElementById("signInSuccessMessage");
    signInSuccessMessage.style.display = "none"
    const emailRegex = /^\w+@\w+\.+\w+$/;
    const signInData = {
        "email":email,
        "password":password
    }
    if (email == ""){
        signInSuccessMessage.textContent = "請輸入電子信箱";
        signInSuccessMessage.style.display = "block";  
    }else if(email.search(emailRegex) == -1){
        signInSuccessMessage.textContent = "請確認電子信箱格式";
        signInSuccessMessage.style.display = "block";  
    }else if(password == ""){
        signInSuccessMessage.textContent = "請輸入密碼";
        signInSuccessMessage.style.display = "block"; 
    }else{
        const signInURL = IP + "api/user/auth"
        fetch(signInURL,{
            method : "PUT",
            headers:{
                "Content-Type" : "application/json"
            },
            body:JSON.stringify(signInData)
        }).then((response) => {            
            return response.json();            
        }).then((result) => {                
            if (result.token != undefined){
                localStorage.setItem("token",result.token)
                memberPage.style.display = "none"
                signInAndSignUp.style.display = "none"
                signOutButton.style.display = "block"
            }else{
                const successMessage = document.getElementById("signInSuccessMessage");
                successMessage.style.display = "none"
                successMessage.textContent = result.message;
                successMessage.style.display = "block";
            }
        }) 
    }                       
}
function signOut(){
    localStorage.removeItem("token")
    signInAndSignUp.style.display = "block"
    signOutButton.style.display = "none"
}
function checkSignInStatus(){
    const signInURL = IP + "api/user/auth"
    let token = localStorage.token
    if (token == undefined){
        return false;
    }else{
        document.body.style.display = "block"
        fetch(signInURL,{
        method : "GET",
        headers : {
            "Authorization": `Bearer ${token}`
        }
        }).then((response) => {
            return response.json();
        }).then((result) =>{
            if (result.data == null){                
                return false;
            }else{                
                signInAndSignUp.style.display = "none";
                signOutButton.style.display = "block";                  
            }
        })
    }            
}
function signUp(){
    const signUpName = document.getElementById("signUpName").value
    const signUpEmail = document.getElementById("signUpEmail").value
    const signUpPassword = document.getElementById("signUpPassword").value
    const successMessage = document.getElementById("successMessage");
    successMessage.style.display = "none"
    const signUpData = {
        "name":signUpName,
        "email":signUpEmail,
        "password":signUpPassword
    }
    const emailRegex = /^\w+@\w+\.+\w+$/;
    if (signUpName == ""){
        successMessage.textContent = "請輸入姓名";
        successMessage.style.display = "block";   
    }else if(signUpEmail == ""){
        successMessage.textContent = "請輸入電子信箱";
        successMessage.style.display = "block";   
    }else if (signUpEmail.search(emailRegex) == -1){
        successMessage.textContent = "請確認電子信箱格式";
        successMessage.style.display = "block";   
    }else if(signUpPassword == ""){
        successMessage.textContent = "請輸入密碼";
        successMessage.style.display = "block";   
    }else{
        const signUpURL = IP + "api/user"
        fetch(signUpURL,{
            method : "POST",
            headers:{
                "Content-Type" : "application/json"
            },
            body:JSON.stringify(signUpData)
        }).then((response) => {
            return response.json();                  
        }).then((result) => {                                
            if(result.ok == true){
                successMessage.textContent = "註冊成功";
                successMessage.style.display = "block";                    
            }else{
                successMessage.textContent = result.message;
                successMessage.style.display = "block";
            }
            return result;
        }).catch((error) => {
            console.log("error");
        })
    }            
}
function switchToSignUp(){
    const signInForm = document.getElementById("signInForm");
    const signUpForm = document.getElementById("signUpForm");
    signInForm.style.display = "none";
    signUpForm.style.display = "block";
    const signUpName = document.getElementById("signUpName");
    signUpName.focus();
}
function switchToSignIn(){
    const signInForm = document.getElementById("signInForm");
    const signUpForm = document.getElementById("signUpForm");
    signInForm.style.display = "block";
    signUpForm.style.display = "none";
    const signInEmailInput = document.getElementById("signInEmailInput");
    signInEmailInput.focus();
}
function redirectToBooking(){
    if (checkSignInStatus() == false){
        memberPage.style.display = "block";              
        switchToSignIn();
    }else{
        return window.location.replace(IP+"booking")
    }
}