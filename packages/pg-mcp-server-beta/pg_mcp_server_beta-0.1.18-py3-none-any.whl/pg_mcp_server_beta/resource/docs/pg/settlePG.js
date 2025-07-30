// 전자결제 연동스크립트
/**
 * SettlePG_v1.2.js
 *
 * postMessage 액션 추가
 *
 */
var Util = {
	isMobile : function() {
		return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
	}
}

var Msg = {
		popup_err: "[헥토파이낸셜] 팝업 차단 설정이 되어 있습니다.\n해제 후 다시 이용해 주세요.",
		pay_err: "[헥토파이낸셜] SETTLE_PG.pay() 호출 시스템 에러",
		validation_err: "[헥토파이낸셜] 호출 파라미터 오류"
	}

var SETTLE_PG = {
	_PG_URL : null,
	_SERVER_CONTEXT : null,
	_LAYER_WIDTH : null,
	_LAYER_HEIGHT : null,
	_DEFAULT_LAYER_WIDTH : 430,
	_DEFAULT_LAYER_HEIGHT : 660,
	_SETTLE_AREA_ID : "SETTLE_AREA_DIV",
	_DIM_ID : "SETTLE_LAYER_DIM",
	_IFRAME_ID : "SETTLE_IFRAME",
	_IFRAME_DIV_ID : "SETTLE_IFRAME_DIV",
	_FORM_ID : "SETTLE_FORM",
	_POPUP_ID : "SETTLE_POPUP",
	_CALLBACK : null,
	// 호출 파리미터명
	_PARAMS : ['mchtId', 'method', 'trdDt', 'trdTm', 'mchtTrdNo', 'mchtName','mchtEName','pmtPrdtNm','trdAmt', 'mchtCustNm','custAcntSumry','expireDt', 'notiUrl', 'nextUrl', 'cancUrl', 'mchtParam',  'cphoneNo', 'email', 'telecomCd', 'prdtTerm', 'mchtCustId', 'taxTypeCd', 'taxAmt', 'vatAmt', 'taxFreeAmt','svcAmt', 'cardType', 'chainUserId', 'cardGb', 'clipCustNm','clipCustCi', 'clipCustPhoneNo','certNotiUrl','skipCd','multiPay', 'autoPayType', 'linkMethod', 'appScheme','custIp','pktHash','corpPayCode', 'corpPayType','cashRcptUIYn','instmtMon','bankCd','csrcIssReqYn','cashRcptPrposDivCd','csrcRegNoDivCd','csrcRegNo'],

	// VALIDATION 파리미터명
	_VALIDATION_MANDATORY_PARAMS : ['mchtId', 'method', 'mchtTrdNo', 'trdDt', 'trdTm', 'trdAmt', 'mchtName', 'notiUrl', 'nextUrl', 'cancUrl', 'pmtPrdtNm', 'pktHash'],
	_VALIDATION_CALLBACK_PARAMS : ['nextUrl', 'cancUrl'],

	// method 정의
	_VALIDATION_METHOD_PARAMS : ['card', 'mobile', 'bank', 'vbank','vbank010', 'tmoney', 'point', 'culturecash', 'booknlife', 'happymoney', 'smartcash', 'teencash', 'corp'],

	makeArea : function(){

		var rand = Math.floor(Math.random() * 99999999);
		this._SETTLE_AREA_ID = "SETTLE_AREA_DIV_"+rand;

		var el = document.createElement("div");
		el.setAttribute("id", this._SETTLE_AREA_ID);

		document.getElementsByTagName("body")[0].appendChild(el);
	},

	makeDim : function(){

		var el = document.createElement("div");
		el.setAttribute("id", this._DIM_ID);
		el.setAttribute("style", "background-color: #000; width:100%; height: 100%; z-index:9999; "
				+"position:fixed; top:0px; left:0px; filter: alpha(Opacity:40) !important; opacity: 0.4 !important; "+
				+"-webkit-opacity: 0.4!important; filter: progid:DXImageTransform.Microsoft.Alpha(Opacity=40);");

		document.getElementById(this._SETTLE_AREA_ID).appendChild(el);
	},

	deleteDim : function(){
		var el = document.getElementById(this._SETTLE_AREA_ID);
		if(el != null){
			if(el.parentNode){
				el.parentNode.removeChild(el);
			}
		}

	},

	pay: function(obj, callback){

		this._CALLBACK = callback;

		var isError = false;

		try{
			if(!this.isNull(obj.env)){
				this._SERVER_CONTEXT = obj.env;
			}else{
				alert("env is null");
				isError = true;
			}


			if(!this.isNull(obj.ui)){

				if(this.isNull(obj.ui.width))
					this._LAYER_WIDTH = this._DEFAULT_LAYER_WIDTH;
				else
					this._LAYER_WIDTH = obj.ui.width;

				if(this.isNull(obj.ui.height))
					this._LAYER_HEIGHT = this._DEFAULT_LAYER_HEIGHT;
				else
					this._LAYER_HEIGHT = obj.ui.height;

				var validation = this.validation(obj);

				if(obj.method == "card"){
					if(obj.methodSub === "direct"){
						// 카드 인증창 직호출
						this._PG_URL = "/card/cardDirect.do";
					}else if(obj.methodSub === "abroad"){
						// 해외카드 결제창 호출
						this._PG_URL = "/card/abroad/main.do";
					}else {
						// 카드 일반
						this._PG_URL = "/card/main.do";
					}
				}else if(obj.method == "bank"){
					this._PG_URL = "/bank/main.do";
				}else if(obj.method == "vbank"){
					if (obj.methodSub === "escro"){
						//무신사 전용(에스크로UI)
						this._PG_URL = "/vbank/escro.do";
					}else{
						//일반
						this._PG_URL = "/vbank/main.do";
					}
				}else if(obj.method == "vbank010"){
					this._PG_URL = "/vbank010/main.do";
				}else if(obj.method == "mobile"){
					if (obj.methodSub === "mtype"){
						//무신사 전용
						this._PG_URL = "/mobile/m/main.do";
					}else{
						//일반
						this._PG_URL = "/mobile/main.do";
					}
				}else if(obj.method == "teencash"){
					this._PG_URL = "/gift/teenCash/main.do";
				}else if(obj.method == "happymoney"){
					this._PG_URL = "/gift/happyMoney/main.do";
				}else if(obj.method == "culturecash"){
					this._PG_URL = "/gift/cultureCash/main.do";
				}else if(obj.method == "smartcash"){
					this._PG_URL = "/gift/smartCash/main.do";
				}else if(obj.method == "booknlife"){
					this._PG_URL = "/gift/booknlife/main.do";
				}else if(obj.method == "tmoney"){
					this._PG_URL = "/tmoney/main.do";
				}else if(obj.method == "point"){
					this._PG_URL = "/point/main.do";
				}else if(obj.method == "corp"){
					this._PG_URL = "/corp/main.do";
				}else{
					this._PG_URL = "undefined";
				}

				if(validation.isSeccess){
					var type = obj.ui.type;

					if(type == "iframe"){
						// iframe
						SETTLE_PG.makeArea();
						SETTLE_PG.makeDim();
						SETTLE_PG.makeIframe();
						SETTLE_PG.makeForm(obj);
					}else if(type == "popup"){
						// popup
						SETTLE_PG.makeForm(obj);
						SETTLE_PG.makePopup();
					}else if(type == "self"){
						// 현재창
						SETTLE_PG.makeForm(obj);
					}else if(type == "blank"){
						// 새로운창
						SETTLE_PG.makeForm(obj);
					}

				}else{
					alert(Msg.validation_err+" ("+validation.errMsg+")");
				}
			}else{
				alert("ui is null");
				isError = true;
			}
		}catch(e){
			console.log(e);
			alert(Msg.pay_err+" ("+e+")");
			isError = true;
			this.deleteDim();

			// 자식창 message remove event
			SETTLE_PG.removePostMessage();
		}

		if(!isError) SETTLE_PG.makeFormSubmit();
	},
	isNull : function(obj){
		if((obj == undefined || obj == '')) return true;
		else return false;
	},

	validation : function(obj){
		var result = new Object();
		result.isSeccess = true;

		var uiType = obj.ui;

		if(!this.isNull(uiType)){

			// callback url 파라미터 체크
			if(uiType.type != 'iframe'){
				for(var i = 0 ; i < this._VALIDATION_CALLBACK_PARAMS.length ; i++){
					if(this.isNull(obj[this._VALIDATION_CALLBACK_PARAMS[i]])){
						result.isSeccess = false;
						result.errMsg = this._VALIDATION_CALLBACK_PARAMS[i] + " is null";
						break;
					}
				}
			}

			for(var i = 0 ; i < this._VALIDATION_MANDATORY_PARAMS.length ; i++){

				// method 속성 체크
				if(this._VALIDATION_MANDATORY_PARAMS[i] == "method"){
					var isFlag = false;
					for(var j = 0 ; j < this._VALIDATION_METHOD_PARAMS.length ; j++){
						if(this._VALIDATION_METHOD_PARAMS[j] == obj[this._VALIDATION_MANDATORY_PARAMS[i]]){
							isFlag = true;
						}
					}

					if(!isFlag){
						result.isSeccess = false;
						result.errMsg = this._VALIDATION_MANDATORY_PARAMS[i] + " is wrong";
						break;
					}
				}

				if(this.isNull(obj[this._VALIDATION_MANDATORY_PARAMS[i]])){
					result.isSeccess = false;
					result.errMsg = this._VALIDATION_MANDATORY_PARAMS[i] + " is null";
					break;
				}

			}

		}else{
			result.isSeccess = false;
			result.errMsg = "ui is null";
		}

		return result;
	},



	makeIframe : function(){

		var el = document.getElementById(this._SETTLE_AREA_ID);
		if(Util.isMobile()){
			var style = document.createElement("iframe");
		    style.setAttribute("frameborder", "0");
		    style.setAttribute("scrolling", "no");
		    style.setAttribute("id", this._IFRAME_ID);
		    style.setAttribute("name", this._IFRAME_ID);
		    style.setAttribute("width", "100%");
		    style.setAttribute("height", "100%");
		    style.setAttribute("align", "center");
		    style.setAttribute("scrolling", "yes");

		    var ifrDiv = document.createElement("div");
		    ifrDiv.setAttribute("id", this._IFRAME_DIV_ID);
		    ifrDiv.setAttribute("style","width:100%; height:100%; position:fixed; top:0; left:0; z-index :100001; background-color: #fff;");
		    ifrDiv.appendChild(style);
		}else{
			var _W = $(window).width();
			var w = Math.floor((_W/2) - (this._LAYER_WIDTH/2) + $(window).scrollLeft());

			var _T = window.innerHeight;
			if(this.isNull(_T)) _T = $(window).height();

			var t = Math.floor((_T-this._LAYER_HEIGHT)/2);

			var style = document.createElement("iframe");
		    style.setAttribute("frameborder", "0");
		    style.setAttribute("scrolling", "no");
		    style.setAttribute("id", this._IFRAME_ID);
		    style.setAttribute("name", this._IFRAME_ID);
		    style.setAttribute("width", this._LAYER_WIDTH);
		    style.setAttribute("height", this._LAYER_HEIGHT);
		    style.setAttribute("align", "center");
		    style.setAttribute("scrolling", "yes");

		    var ifrDiv = document.createElement("div");
		    ifrDiv.setAttribute("id", this._IFRAME_DIV_ID);
		    ifrDiv.setAttribute("style","height:"+this._LAYER_HEIGHT+"px; position:fixed; top:"+ (t / _T) * 100 +"%; left:"+(w / _W) * 100+"%; z-index :100001; background-color: #fff;");
		    ifrDiv.appendChild(style);
		}
	    el.appendChild(ifrDiv);


	    if(window.addEventListener){
			window.removeEventListener("resize", this.iframeResize, false);
		}else if(window.attachEvent){
			window.detachEvent("resize", this.iframeResize, false);
		}

	    // 자식창 message add event
	    SETTLE_PG.addPostMessage();

	},

	iframeResize : function(){
		var el = document.getElementById(SETTLE_PG._IFRAME_DIV_ID);
    	if(el != null){
	    	var _W = $(window).width();
	    	var w = Math.floor((_W/2) - (SETTLE_PG._LAYER_WIDTH/2) + $(window).scrollLeft());

	    	var _T = window.innerHeight;
			if(this.isNull(_T)) _T = $(window).height();

			var t = Math.floor((_T - SETTLE_PG._LAYER_HEIGHT)/2);
			el.style.top = ( t / _T) * 100 + "%";
			el.style.left = ( w / _W) * 100 + "%";
    	}
	},

	closeIframe : function(data){

		this.deleteDim();

		// postMessage action Field 삭제
		//delete data.action;

		this._CALLBACK(data);

		// 자식창 message remove event
		SETTLE_PG.removePostMessage();
	},

	resizeIframe : function(data){
		this._LAYER_WIDTH = data.width;
		var el = document.getElementById(this._IFRAME_ID);
		el.setAttribute("width", this._LAYER_WIDTH);

		this.iframeResize();
	},

	returnSizeIframe : function(){
		this._LAYER_WIDTH = this._DEFAULT_LAYER_WIDTH;
		var el = document.getElementById(this._IFRAME_ID);
		el.setAttribute("width", this._LAYER_WIDTH);

		this.iframeResize();
	},

	makeForm : function(obj){

		var el = document.getElementById(this._IFRAME_ID);

		el = document.getElementsByTagName("body")[0];

		var settleForm = document.createElement("form");
		settleForm.setAttribute("id", this._FORM_ID);
		settleForm.setAttribute("name", this._FORM_ID);
		settleForm.setAttribute("method", "POST");
		settleForm.setAttribute("action", this._SERVER_CONTEXT + this._PG_URL);

		var type = obj.ui.type;

		if(type == "iframe"){
			// iframe
			settleForm.setAttribute("target", this._IFRAME_ID);
			settleForm.appendChild(this.makeFormInput("height", this._LAYER_HEIGHT));

		}else if(type == "popup"){
			// popup
			settleForm.setAttribute("target", this._POPUP_ID);
		}else if(type == "self"){
			// 현재창
			settleForm.setAttribute("target", "_self");
		}else if(type == "blank"){
			// 새로운창
			settleForm.setAttribute("target", "_blank");
		}

		settleForm.appendChild(this.makeFormInput('type', type));

		for(var i = 0 ; i < this._PARAMS.length ; i++){
			var tmp = obj[this._PARAMS[i]];
			if(this.isNull(tmp)) tmp = "";


			settleForm.appendChild(this.makeFormInput(this._PARAMS[i], tmp));
		}

		el.appendChild(settleForm);

	},

	makeFormInput : function(name, value){

		var settleInput = document.createElement("input");

		settleInput.setAttribute("type", "hidden");
		settleInput.setAttribute("name", name);
		settleInput.setAttribute("value", value);

		return settleInput;
	},

	makeFormSubmit : function(){
		var el = document.getElementById(this._FORM_ID);
		if(el != null){
			el.submit();

			setTimeout(function(){
				if(el.parentNode){
					el.parentNode.removeChild(el);
				}
			}, 1000);
		}
	},

	makePopup : function(){
		var userAgent = new String(navigator.userAgent);
		var windowStatus = '';

		var xpos = (screen.width - this._LAYER_WIDTH ) / 2;
		var ypos = (screen.width - this._LAYER_HEIGHT ) / 6;

		if (userAgent.indexOf('Trident') > 0) {
			if (userAgent.indexOf('Trident/4.0') > 0){
				windowStatus = 'left='+xpos+', top='+ypos+', height='+this._LAYER_HEIGHT+', width='+this._LAYER_WIDTH+', location=no, menubar=no, scrollbars=yes, status=no, titlebar=no, toolbar=no, resizable=no';
			}else{
				windowStatus = 'left='+xpos+', top='+ypos+', height='+this._LAYER_HEIGHT+', width='+this._LAYER_WIDTH+', location=no, menubar=no, scrollbars=yes, status=no, titlebar=no, toolbar=no, resizable=no';
			}
		}
		else if (userAgent.indexOf('AppleWebKit') > 0 && userAgent.indexOf('Chrome') == -1) {
			windowStatus = 'left='+xpos+', top='+ypos+', height='+this._LAYER_HEIGHT+', width='+this._LAYER_WIDTH+', location=no, menubar=no, scrollbars=auto, status=no, titlebar=no, toolbar=no, resizable=no';
		}
		/*
		 * else if (userAgent.indexOf('Edge') > 0 ) { alert("Windwos10의 브라우저
		 * 엣지(Edge) 사용 시 결제 이용이 불가하므로 Windwos10에 내에 포함된 인터넷 익스플로러(IE)11 또는
		 * Chrome 브라우저를 이용 바랍니다."); return false; }
		 */
		else {
			windowStatus = 'left='+xpos+', top='+ypos+', height='+this._LAYER_HEIGHT+', width='+this._LAYER_WIDTH+', location=no, menubar=no, scrollbars=auto, status=no, titlebar=no, toolbar=no, resizable=no';
		}

		var payPopup = window.open('', this._POPUP_ID, windowStatus);

		setTimeout(function(){
			if (payPopup == null) {
					alert(Msg.popup_err)
			}
		}, 1000);
	},

	addPostMessage : function(){
		if(window.addEventListener){
			window.addEventListener("message", this.procPostMessage, false);
		}else if(window.attachEvent){
			window.attachEvent("onmessage", this.procPostMessage, false);
		}
	},

	removePostMessage : function(){
		if(window.addEventListener){
			window.removeEventListener("message", this.procPostMessage, false);
		}else if(window.attachEvent){
			window.detachEvent("onmessage", this.procPostMessage, false);
		}
	},

	procPostMessage : function(event){
		let data;
		try {
			data = JSON.parse(event.data);
		} catch (e) {
			console.log(e);
		}

		if (data && data.action === "HECTO_IFRAME_CLOSE") {
			SETTLE_PG.closeIframe(data.params);
		} else if (data && data.action === "HECTO_IFRAME_RESIZE") {
			SETTLE_PG.resizeIframe(data.params);
		} else if (data && data.action === "HECTO_IFRAME_RETURNSIZE") {
			SETTLE_PG.returnSizeIframe();
		}
	}
}