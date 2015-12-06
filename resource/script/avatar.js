$(function(){
	$('.body_wrap.avatar .load_wrap .coupon-image[data-fid]').each(function(){
		var item	= $(this);
		var fid		= item.attr('data-fid');
		var avatar	= item.attr('data-avatar');
		if (avatar != ''){
			avatar = 'http://wx.qlogo.cn/mmopen/'+ avatar +'/96';
		} else{
			avatar = '/static/images/noavatar_small.jpg';
		}
		
		item.html(
			'<a href="site.php?act=fans&do=profile&fid='+fid+'" title="编辑信息">'+
				'<img src="'+avatar+'" onerror="this.src=\'resource/image/noavatar_small.jpg\'" />'+
			'</a>'+
			'<div class="photo-intro">'+
				'<div class="popover_inner">'+
					'<a href="site.php?act=fans&do=message&fid='+fid+'" title="消息记录"><i class="icon-envelope-alt"></i></a>'+
					'<a href="site.php?act=analysis&do=display&fid='+fid+'" title="领券记录"><i class="icon-ticket"></i></a>'+
				//	'<a href="site.php?act=analysis&do=coupon&fid='+fid+'" title="领券分析"><i class="icon-bar-chart"></i></a>'+
					'<a href="site.php?act=analysis&do=credit&fid='+fid+'" title="金币记录"><i class="icon-certificate"></i></a>'+
				//	'<a href="site.php?act=fans&do=member&come=scanuser&which='+fid+'" title="邀请记录"><i class="icon-cogs"></i></a>'+
				//	'<a href="site.php?act=analysis&do=mettings&fid='+fid+'" title="签到记录"><i class="icon-calendar-empty"></i></a>'+
				//	'<a href="site.php?act=analysis&do=shopping&fid='+fid+'" title="礼品记录"><i class="icon-gift"></i></a>'+
				'</div>'+
				'<i class="popover_arrow"></i>'+
				'<i class="popover_arrow_in"></i>'+
			'</div>'
		);
	});
});