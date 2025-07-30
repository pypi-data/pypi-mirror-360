// 내통장결제 연동스크립트
var serverContext = 'https://ezauth.settlebank.co.kr';
//var serverContext = 'https://stgezauth.settlebank.co.kr:8080';

var Msg = {	
	dev_err1: "팝업 차단 설정이 되어 있습니다.\n해제 후 다시 이용해 주십시오."
}

var Util = {
	isMobile : function() {
		return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
	}	
}

var SettlePay = {	
	getUrl : function(obj){
		var processType;
		var url = "";
		try{
			processType = obj.processType.value;
			if(processType == "D" || processType == "M" || processType == "A"){
				//url = serverContext + "/std/init.do";
				url = serverContext + "/init.do";
			}else if(processType == "W"){//휘슬전용
				url = serverContext + "/whistle/init.do";
			}
		}catch(e){
			processType='D';
			url = serverContext + "/verifyMember.do";
		}

		return url;
	}
	,pay : function(obj){
		var viewType;
		try{
			viewType = obj.viewType.value;
		}catch(e){
			viewType='popup';
		}
		
		viewType == null ? 'popup':viewType;
		if(viewType == 'popup'){
			this.popup(obj);
		}else if(viewType == 'self'){
			this.self(obj);
		}
	}
		
	// 결제창 호출
	,execute : function(obj){
		if (Util.isMobile()){
			SettlePay.self(obj);
		}else{
			SettlePay.popup(obj);
		}
	}
	
	// 서비스관리창 호출
	,svc_execute : function(obj){
		if (Util.isMobile()){
			SettlePay.svc_mobile(obj);
		}else{
			SettlePay.svc_popup(obj);
		}
	}
		
	// 팝업
	,popup : function(obj) {
		var userAgent = new String(navigator.userAgent);
		var windowStatus = '';
		if (userAgent.indexOf('Trident') > 0) {
			if (userAgent.indexOf('Trident/4.0') > 0){
				windowStatus = 'left=100, top=100, height=610, width=420, location=no, menubar=no, scrollbars=yes, status=no, titlebar=no, toolbar=no, resizable=no';
			}else{
				windowStatus = 'left=100, top=100, height=610, width=420, location=no, menubar=no, scrollbars=yes, status=no, titlebar=no, toolbar=no, resizable=no';	
			}				
		} 
		else if (userAgent.indexOf('AppleWebKit') > 0 && userAgent.indexOf('Chrome') == -1) {
			windowStatus = 'left=100, top=100, height=610, width=420, location=no, menubar=no, scrollbars=auto, status=no, titlebar=no, toolbar=no, resizable=no';
		} 
		/*else if (userAgent.indexOf('Edge') > 0 ) {
			alert("Windwos10의 브라우저 엣지(Edge) 사용 시 결제 이용이 불가하므로 Windwos10에 내에 포함된 인터넷 익스플로러(IE)11 또는 Chrome 브라우저를 이용 바랍니다.");
			return false;
		}*/
		else {
			windowStatus = 'left=100, top=100, height=610, width=420, location=no, menubar=no, scrollbars=auto, status=no, titlebar=no, toolbar=no, resizable=no';
		}
		stdpaywin = window.open('', obj.name, windowStatus); 
			
		setTimeout(function(){
			if (stdpaywin == null) {
					alert(Msg.dev_err1)
			}     
		}, 1000)
		
		obj.action = SettlePay.getUrl(obj);		
		obj.method='POST';
		obj.target=obj.name;			
		obj.submit();
	}
	,self : function(obj) {
		obj.action = SettlePay.getUrl(obj);
		obj.method='POST';
		obj.target='_self';
		obj.submit();
	}
	,mobile : function(obj) {			
		stdpaywin = window.open('', obj.name, ''); 
		setTimeout(function(){
			if (stdpaywin == null) {
					alert(Msg.dev_err1)
			}     
		}, 1000)
			
		obj.action = SettlePay.getUrl(obj);
		obj.method='POST';
		obj.target=obj.name;
		obj.submit();
	}
	,cashRcptInfo : function(obj){
		obj.action = serverContext + "/cashRcptInfo.do";
		obj.method='POST';
		obj.target='_blank';
		obj.submit();
	},svc_popup : function (obj){
		var userAgent = new String(navigator.userAgent);
		var windowStatus = '';
		if (userAgent.indexOf('Trident') > 0) {
			if (userAgent.indexOf('Trident/4.0') > 0){
				windowStatus = 'left=100, top=100, height=610, width=420, location=no, menubar=no, scrollbars=yes, status=no, titlebar=no, toolbar=no, resizable=no';
			}else{
				windowStatus = 'left=100, top=100, height=610, width=420, location=no, menubar=no, scrollbars=yes, status=no, titlebar=no, toolbar=no, resizable=no';	
			}				
		} 
		else if (userAgent.indexOf('AppleWebKit') > 0 && userAgent.indexOf('Chrome') == -1) {
			windowStatus = 'left=100, top=100, height=610, width=420, location=no, menubar=no, scrollbars=auto, status=no, titlebar=no, toolbar=no, resizable=no';
		}
		else {
			windowStatus = 'left=100, top=100, height=610, width=420, location=no, menubar=no, scrollbars=auto, status=no, titlebar=no, toolbar=no, resizable=no';
		}
		stdpaywin = window.open('', obj.name, windowStatus); 
		
		obj.action = "/std/iaDirect.do";		
		obj.method='POST';
		obj.target=obj.name;			
		obj.submit();
	},svc_mobile : function(obj) {			
		stdpaywin = window.open('', obj.name, ''); 
		setTimeout(function(){
			if (stdpaywin == null) {
					alert(Msg.dev_err1)
			}     
		}, 1000)
			
		obj.action = "/std/iaDirect.do";
		obj.method='POST';
		obj.target=obj.name;
		obj.submit();
	}
	
}