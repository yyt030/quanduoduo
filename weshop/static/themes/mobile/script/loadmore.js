var costclass = new Array(5);costclass['特价']	= '1';costclass['满减']	= '2';costclass['折扣']	= '3';costclass['抵现']	= '4';costclass['免单']	= '5';var urlParam = "";var pageMark = 0;var loadtype = "";$(document).ready(function() {	//绑定加载事件	$('.more_wrap .load_more').click(function(){		load_discount();	}).click();		//打开下拉菜单	$('.filt_wrap .load_wrap span.select').click(function(){		$('.menu_wrap.'+$(this).data('type')).slideToggle().siblings('.menu_wrap').hide();	});		//绑定下拉菜单	$('.menu_wrap dl').each(function($item,$data){		$item = $(this);		$type = $(this).parent().data('type');				//二级分类展开或闭合		$('h5',$item).click(function(){			$item.find('dd').slideToggle();			$item.siblings().find('dd').slideUp();		});		//点击筛选后动态加载		$('h4',$item).data('type',$type).click(function(){			$('.filt_wrap span.select.'+ $(this).data('type') +' a').text($(this).text());			setRecord($(this).data('type')+'2','');			save_urlparam($(this).data('type')+'1',$(this).text());			$('.menu_wrap').slideUp();			$('#body_wrap .load_wrap').remove();			load_discount();		});		$('li',$item).data('type',$type).click(function(){			$('.filt_wrap span.select.'+ $(this).data('type') +' a').text($(this).text());			setRecord($(this).data('type')+'1','');			save_urlparam($(this).data('type')+'2',$(this).text());			$('.menu_wrap').slideUp();			$('#body_wrap .load_wrap').remove();			load_discount();		});	});});//加载信息function load_discount(type,param){	if(type=='industry1'||type=='industry2'||type=='sorttype1'||type=='district1'||type=='sortrank1'){		$('#body_wrap .load_wrap').remove();		save_urlparam(type,param);	}	//更新请求参数	if(urlParam==''){		load_urlparam();	};		////检查定位信息	//if (getRecord('district1')!='范围'){	//	var time = new Date().getTime()/1000;	//	if (getCookie('__latlngtime')==null||parseInt(getCookie('__latlngtime'))+900<time){	//		$('#position').show();	//		navigator.geolocation.getCurrentPosition(function(position){	//			setCookie('__lat',position.coords.latitude);	//			setCookie('__lng',position.coords.longitude);	//			setCookie('__latlngtime',time);	//			$('#position').hide();	//			show_discount();	//		},function(error){	//			document.getElementById('placewhere').innerHTML = '定位失败';	//			return;	//		});	//	} else{	//		show_discount();	//	}	//} else{	//	show_discount();	//}	show_discount()}//插入列表function show_discount(){	//加载一页信息	$('.more_wrap .load_tips').show().siblings().hide();//加载中	$.getJSON(queryURL +urlParam +'&page='+(pageMark++), function(data) {		if (data.type == 'ajax'){			for (property in data.message[0]) {				//发行数量				if (data.message[0][property].number== 0){					data.message[0][property].number = data.message[0][property].total;				}				$('<div class="load_wrap activity">'+				'<a href="'+placeURL+'?did='+data.message[0][property].did+'">'+					'<div class="coupon-image">'+						'<img src="'+imageURL+data.message[1][data.message[0][property].bid].thumb+'" />'+					'</div>'+					'<div class="coupon-intro">'+						'<p class="title">'+ data.message[0][property].title +'</p>'+						'<p class="count">'+ '每天<b>'+data.message[0][property].number+'</b>份<span>'+ data.message[0][property].count +'人已领</span></p>'+						'<p class="brand">'+ data.message[1][data.message[0][property].bid].brand + '</p>'+					'</div>'+					'<div class="coupon-class">'+						'<i class="state">领券</i>'+					'</div>'+				'</a>'+				'</div>').appendTo('#body_wrap');			}			$('.more_wrap .load_more').show().siblings().hide();//还有更多		} else{			$('.more_wrap .load_none').show().siblings().hide();//没有了		}	});}//加载参数function load_urlparam(){	if (getRecord('industry1')){		$('.filt_wrap span.select.industry a').text(getRecord('industry1'));		urlParam+= '&industry1=' +getRecord('industry1');	}	if (getRecord('industry2')){		$('.filt_wrap span.select.industry a').text(getRecord('industry2'));		urlParam+= '&industry2=' +getRecord('industry2');	}	if (getRecord('sorttype1')){		$('.filt_wrap span.select.sorttype a').text(getRecord('sorttype1'));		urlParam+= '&sorttype1=' +getRecord('sorttype1');	}	if (getRecord('district1')){		$('.filt_wrap span.select.district a').text(getRecord('district1'));		urlParam+= '&district1=' +getRecord('district1');	}	if (getRecord('sortrank1')){		$('.filt_wrap span.select.sortrank a').text(getRecord('sortrank1'));		urlParam+= '&sortrank1=' +getRecord('sortrank1');	}}//设置参数function save_urlparam(type,param){	if(param!=''){		setRecord(type,param);		urlParam = '';		pageMark = 0;		load_urlparam();	};}function getRecord(name){	name = loadtype+name;	return window.sessionStorage.getItem(name);        // 取值}function setRecord(name,value){	name = loadtype+name;	return window.sessionStorage.setItem(name,value);  // 赋值}function getCookie(name){	name = loadtype+name;	var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");	if(arr=document.cookie.match(reg)) return unescape(arr[2]);	else return null;}function setCookie(name,value){	name = loadtype+name;	var days = days || 7;	var path = path?location.pathname:'/';	var date = new Date();	date.setTime(date.getTime() + days*24*3600*1000);	document.cookie = name + "=" + escape (value) + ";path=" + path + ";domain=;expires=" + date.toGMTString();}