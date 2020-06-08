
//최저가 갱신 알림 받기 checkbox
function mypage_subscription_condition1(){
	alert("check box 클릭");
}

//가격 변동 소식 알림 받기 check box
function mypage_subscription_condition2(){
	alert("check box 클릭");
}

//카카오로 알림받기
function mypage_subscription_method1(){
	alert("카카오");	
}

//이메일로 알림받기
function mypage_subscription_method2(){
	alert("이메일");	
}

//휴대폰 푸시 알림으로 알림받기
function mypage_subscription_method3(){
	alert("휴대폰 푸시 알림");	
}

//북마크 제거
function mypage_bookmarks_delete(product){
	alert(product+ "북마크 제거");
}

function product_search(product){
	alert(product+"검색");
}


function news_click(){
	alert("news 클릭");
}

function product_subscription(){
	alert("sub");
}



function search_box_focused(){
	//var check = document.getElementById("test");
	var el = document.getElementById("home-dropdown");
	el.style.display = "inline";
}
function home_dropdown_clicked(){
	document.getElementById("search-box-id").focus();
}

