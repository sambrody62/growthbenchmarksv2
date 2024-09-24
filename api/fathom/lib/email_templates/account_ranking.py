def generate_ranking_bullets(ranking):
    account_name = ranking['account_name']
    ranking_bullets = ""
    for metric in ['cpc','ctr','cpm']:
        long_provider = 'facebook'
        if (ranking['provider_id'] == 'google'):
            long_provider = 'google'

        account_link=f"https://growthbenchmarks.com/{long_provider}/{ranking['account_id']}/{metric}"
        
        RANKING_BULLET = f"""<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="min-width:100%;">
    <tbody class="mcnTextBlockOuter">
        <tr>
            <td valign="top" class="mcnTextBlockInner" style="padding-top:9px;">
              	<!--[if mso]>
				<table align="left" border="0" cellspacing="0" cellpadding="0" width="100%" style="width:100%;">
				<tr>
				<![endif]-->
			    
				<!--[if mso]>
				<td valign="top" width="600" style="width:600px;">
				<![endif]-->
                <table align="left" border="0" cellpadding="0" cellspacing="0" style="max-width:100%; min-width:100%;" width="100%" class="mcnTextContentContainer">
                    <tbody><tr>
                        
                        <td valign="top" class="mcnTextContent" style="padding: 0px 18px 9px; line-height: 125%;">
                        
                            <div style="text-align: left;">&#8226;&nbsp;<span style="font-size:18px"><span style="color:#000000"><span style="font-family:space grotesk,lucida,helvetica,arial,sans-serif"><a href="{account_link}" target="_blank">{account_name}</a> has a<strong> {metric.upper()}  </strong>of<strong> {round(float(ranking.get(metric,0)),2)} </strong>and is ranked "<strong> {ranking.get(metric + '_rank_text')}</strong>"</span></span></span></div>

                        </td>
                    </tr>
                </tbody></table>
				<!--[if mso]>
				</td>
				<![endif]-->
                
				<!--[if mso]>
				</tr>
				</table>
				<![endif]-->
            </td>
        </tr>
    </tbody>
</table>"""
        ranking_bullets += RANKING_BULLET
    return ranking_bullets

def account_ranking_email(account_rankings):
	html_ranking_list = ''.join([generate_ranking_bullets(x) for x in account_rankings])

	TEMPLATE_PART_1 = """<!doctype html>
	<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
		<head>
			<!-- NAME: EDUCATE -->
			<!--[if gte mso 15]>
			<xml>
				<o:OfficeDocumentSettings>
				<o:AllowPNG/>
				<o:PixelsPerInch>96</o:PixelsPerInch>
				</o:OfficeDocumentSettings>
			</xml>
			<![endif]-->
			<meta charset="UTF-8">
			<meta http-equiv="X-UA-Compatible" content="IE=edge">
			<meta name="viewport" content="width=device-width, initial-scale=1">
			<title>Growthbenchmarks.com - Where are your accounts ranked?</title>
			
		<style type="text/css">
			p{
				margin:10px 0;
				padding:0;
			}
			table{
				border-collapse:collapse;
			}
			h1,h2,h3,h4,h5,h6{
				display:block;
				margin:0;
				padding:0;
			}
			img,a img{
				border:0;
				height:auto;
				outline:none;
				text-decoration:none;
			}
			body,#bodyTable,#bodyCell{
				height:100%;
				margin:0;
				padding:0;
				width:100%;
			}
			.mcnPreviewText{
				display:none !important;
			}
			#outlook a{
				padding:0;
			}
			img{
				-ms-interpolation-mode:bicubic;
			}
			table{
				mso-table-lspace:0pt;
				mso-table-rspace:0pt;
			}
			.ReadMsgBody{
				width:100%;
			}
			.ExternalClass{
				width:100%;
			}
			p,a,li,td,blockquote{
				mso-line-height-rule:exactly;
			}
			a[href^=tel],a[href^=sms]{
				color:inherit;
				cursor:default;
				text-decoration:none;
			}
			p,a,li,td,body,table,blockquote{
				-ms-text-size-adjust:100%;
				-webkit-text-size-adjust:100%;
			}
			.ExternalClass,.ExternalClass p,.ExternalClass td,.ExternalClass div,.ExternalClass span,.ExternalClass font{
				line-height:100%;
			}
			a[x-apple-data-detectors]{
				color:inherit !important;
				text-decoration:none !important;
				font-size:inherit !important;
				font-family:inherit !important;
				font-weight:inherit !important;
				line-height:inherit !important;
			}
			.templateContainer{
				max-width:600px !important;
			}
			a.mcnButton{
				display:block;
			}
			.mcnImage,.mcnRetinaImage{
				vertical-align:bottom;
			}
			.mcnTextContent{
				word-break:break-word;
			}
			.mcnTextContent img{
				height:auto !important;
			}
			.mcnDividerBlock{
				table-layout:fixed !important;
			}
		/*
		@tab Page
		@section Heading 1
		@style heading 1
		*/
			h1{
				/*@editable*/color:#000000;
				/*@editable*/font-family:'Lucida Sans Unicode', 'Lucida Grande', sans-serif;
				/*@editable*/font-size:24px;
				/*@editable*/font-style:normal;
				/*@editable*/font-weight:bold;
				/*@editable*/line-height:200%;
				/*@editable*/letter-spacing:normal;
				/*@editable*/text-align:left;
			}
		/*
		@tab Page
		@section Heading 2
		@style heading 2
		*/
			h2{
				/*@editable*/color:#000000;
				/*@editable*/font-family:'Lucida Sans Unicode', 'Lucida Grande', sans-serif;
				/*@editable*/font-size:21px;
				/*@editable*/font-style:normal;
				/*@editable*/font-weight:bold;
				/*@editable*/line-height:200%;
				/*@editable*/letter-spacing:normal;
				/*@editable*/text-align:left;
			}
		/*
		@tab Page
		@section Heading 3
		@style heading 3
		*/
			h3{
				/*@editable*/color:#000000;
				/*@editable*/font-family:'Lucida Sans Unicode', 'Lucida Grande', sans-serif;
				/*@editable*/font-size:18px;
				/*@editable*/font-style:normal;
				/*@editable*/font-weight:bold;
				/*@editable*/line-height:200%;
				/*@editable*/letter-spacing:normal;
				/*@editable*/text-align:left;
			}
		/*
		@tab Page
		@section Heading 4
		@style heading 4
		*/
			h4{
				/*@editable*/color:#000000;
				/*@editable*/font-family:'Lucida Sans Unicode', 'Lucida Grande', sans-serif;
				/*@editable*/font-size:16px;
				/*@editable*/font-style:italic;
				/*@editable*/font-weight:normal;
				/*@editable*/line-height:150%;
				/*@editable*/letter-spacing:normal;
				/*@editable*/text-align:left;
			}
		/*
		@tab Header
		@section Header Container Style
		*/
			#templateHeader{
				/*@editable*/background-color:#ffeef0;
				/*@editable*/background-image:none;
				/*@editable*/background-repeat:repeat-x;
				/*@editable*/background-position:center;
				/*@editable*/background-size:contain;
				/*@editable*/border-top:0;
				/*@editable*/border-bottom:0;
				/*@editable*/padding-top:0px;
				/*@editable*/padding-bottom:0px;
			}
		/*
		@tab Header
		@section Header Interior Style
		*/
			.headerContainer{
				/*@editable*/background-color:#transparent;
				/*@editable*/background-image:none;
				/*@editable*/background-repeat:no-repeat;
				/*@editable*/background-position:center;
				/*@editable*/background-size:cover;
				/*@editable*/border-top:0;
				/*@editable*/border-bottom:0;
				/*@editable*/padding-top:0;
				/*@editable*/padding-bottom:0;
			}
		/*
		@tab Header
		@section Header Text
		*/
			.headerContainer .mcnTextContent,.headerContainer .mcnTextContent p{
				/*@editable*/color:#757575;
				/*@editable*/font-family:Helvetica;
				/*@editable*/font-size:16px;
				/*@editable*/line-height:150%;
				/*@editable*/text-align:left;
			}
		/*
		@tab Header
		@section Header Link
		*/
			.headerContainer .mcnTextContent a,.headerContainer .mcnTextContent p a{
				/*@editable*/color:#007C89;
				/*@editable*/font-weight:normal;
				/*@editable*/text-decoration:underline;
			}
		/*
		@tab Body
		@section Body Container Style
		*/
			#templateBody{
				/*@editable*/background-color:#ffffff;
				/*@editable*/background-image:none;
				/*@editable*/background-repeat:no-repeat;
				/*@editable*/background-position:center;
				/*@editable*/background-size:cover;
				/*@editable*/border-top:0;
				/*@editable*/border-bottom:0;
				/*@editable*/padding-top:60px;
				/*@editable*/padding-bottom:90px;
			}
		/*
		@tab Body
		@section Body Interior Style
		*/
			.bodyContainer{
				/*@editable*/background-color:#transparent;
				/*@editable*/background-image:none;
				/*@editable*/background-repeat:no-repeat;
				/*@editable*/background-position:center;
				/*@editable*/background-size:cover;
				/*@editable*/border-top:0;
				/*@editable*/border-bottom:0;
				/*@editable*/padding-top:0;
				/*@editable*/padding-bottom:0;
			}
		/*
		@tab Body
		@section Body Text
		*/
			.bodyContainer .mcnTextContent,.bodyContainer .mcnTextContent p{
				/*@editable*/color:#3c3c3c;
				/*@editable*/font-family:'Lucida Sans Unicode', 'Lucida Grande', sans-serif;
				/*@editable*/font-size:18px;
				/*@editable*/line-height:150%;
				/*@editable*/text-align:left;
			}
		/*
		@tab Body
		@section Body Link
		*/
			.bodyContainer .mcnTextContent a,.bodyContainer .mcnTextContent p a{
				/*@editable*/color:#eb6329;
				/*@editable*/font-weight:normal;
				/*@editable*/text-decoration:underline;
			}
		/*
		@tab Footer
		@section Footer Style
		*/
			#templateFooter{
				/*@editable*/background-color:#000000;
				/*@editable*/background-image:none;
				/*@editable*/background-repeat:no-repeat;
				/*@editable*/background-position:center;
				/*@editable*/background-size:cover;
				/*@editable*/border-top:0;
				/*@editable*/border-bottom:0;
				/*@editable*/padding-top:30px;
				/*@editable*/padding-bottom:90px;
			}
		/*
		@tab Footer
		@section Footer Interior Style
		*/
			.footerContainer{
				/*@editable*/background-color:#transparent;
				/*@editable*/background-image:none;
				/*@editable*/background-repeat:no-repeat;
				/*@editable*/background-position:center;
				/*@editable*/background-size:cover;
				/*@editable*/border-top:0;
				/*@editable*/border-bottom:0;
				/*@editable*/padding-top:0;
				/*@editable*/padding-bottom:0;
			}
		/*
		@tab Footer
		@section Footer Text
		*/
			.footerContainer .mcnTextContent,.footerContainer .mcnTextContent p{
				/*@editable*/color:#FFFFFF;
				/*@editable*/font-family:Tahoma, Verdana, Segoe, sans-serif;
				/*@editable*/font-size:12px;
				/*@editable*/line-height:150%;
				/*@editable*/text-align:center;
			}
		/*
		@tab Footer
		@section Footer Link
		*/
			.footerContainer .mcnTextContent a,.footerContainer .mcnTextContent p a{
				/*@editable*/color:#FFFFFF;
				/*@editable*/font-weight:normal;
				/*@editable*/text-decoration:underline;
			}
		@media only screen and (min-width:768px){
			.templateContainer{
				width:600px !important;
			}

	}	@media only screen and (max-width: 480px){
			body,table,td,p,a,li,blockquote{
				-webkit-text-size-adjust:none !important;
			}

	}	@media only screen and (max-width: 480px){
			body{
				width:100% !important;
				min-width:100% !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnRetinaImage{
				max-width:100% !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnImage{
				width:100% !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnCartContainer,.mcnCaptionTopContent,.mcnRecContentContainer,.mcnCaptionBottomContent,.mcnTextContentContainer,.mcnBoxedTextContentContainer,.mcnImageGroupContentContainer,.mcnCaptionLeftTextContentContainer,.mcnCaptionRightTextContentContainer,.mcnCaptionLeftImageContentContainer,.mcnCaptionRightImageContentContainer,.mcnImageCardLeftTextContentContainer,.mcnImageCardRightTextContentContainer,.mcnImageCardLeftImageContentContainer,.mcnImageCardRightImageContentContainer{
				max-width:100% !important;
				width:100% !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnBoxedTextContentContainer{
				min-width:100% !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnImageGroupContent{
				padding:9px !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnCaptionLeftContentOuter .mcnTextContent,.mcnCaptionRightContentOuter .mcnTextContent{
				padding-top:9px !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnImageCardTopImageContent,.mcnCaptionBottomContent:last-child .mcnCaptionBottomImageContent,.mcnCaptionBlockInner .mcnCaptionTopContent:last-child .mcnTextContent{
				padding-top:18px !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnImageCardBottomImageContent{
				padding-bottom:9px !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnImageGroupBlockInner{
				padding-top:0 !important;
				padding-bottom:0 !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnImageGroupBlockOuter{
				padding-top:9px !important;
				padding-bottom:9px !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnTextContent,.mcnBoxedTextContentColumn{
				padding-right:18px !important;
				padding-left:18px !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcnImageCardLeftImageContent,.mcnImageCardRightImageContent{
				padding-right:18px !important;
				padding-bottom:0 !important;
				padding-left:18px !important;
			}

	}	@media only screen and (max-width: 480px){
			.mcpreview-image-uploader{
				display:none !important;
				width:100% !important;
			}

	}	@media only screen and (max-width: 480px){
		/*
		@tab Mobile Styles
		@section Heading 1
		@tip Make the first-level headings larger in size for better readability on small screens.
		*/
			h1{
				/*@editable*/font-size:24px !important;
				/*@editable*/line-height:125% !important;
			}

	}	@media only screen and (max-width: 480px){
		/*
		@tab Mobile Styles
		@section Heading 2
		@tip Make the second-level headings larger in size for better readability on small screens.
		*/
			h2{
				/*@editable*/font-size:24px !important;
				/*@editable*/line-height:125% !important;
			}

	}	@media only screen and (max-width: 480px){
		/*
		@tab Mobile Styles
		@section Heading 3
		@tip Make the third-level headings larger in size for better readability on small screens.
		*/
			h3{
				/*@editable*/font-size:21px !important;
				/*@editable*/line-height:150% !important;
			}

	}	@media only screen and (max-width: 480px){
		/*
		@tab Mobile Styles
		@section Heading 4
		@tip Make the fourth-level headings larger in size for better readability on small screens.
		*/
			h4{
				/*@editable*/font-size:18px !important;
				/*@editable*/line-height:150% !important;
			}

	}	@media only screen and (max-width: 480px){
		/*
		@tab Mobile Styles
		@section Boxed Text
		@tip Make the boxed text larger in size for better readability on small screens. We recommend a font size of at least 16px.
		*/
			.mcnBoxedTextContentContainer .mcnTextContent,.mcnBoxedTextContentContainer .mcnTextContent p{
				/*@editable*/font-size:16px !important;
				/*@editable*/line-height:150% !important;
			}

	}	@media only screen and (max-width: 480px){
		/*
		@tab Mobile Styles
		@section Header Text
		@tip Make the header text larger in size for better readability on small screens.
		*/
			.headerContainer .mcnTextContent,.headerContainer .mcnTextContent p{
				/*@editable*/font-size:16px !important;
				/*@editable*/line-height:150% !important;
			}

	}	@media only screen and (max-width: 480px){
		/*
		@tab Mobile Styles
		@section Body Text
		@tip Make the body text larger in size for better readability on small screens. We recommend a font size of at least 16px.
		*/
			.bodyContainer .mcnTextContent,.bodyContainer .mcnTextContent p{
				/*@editable*/font-size:16px !important;
				/*@editable*/line-height:150% !important;
			}

	}	@media only screen and (max-width: 480px){
		/*
		@tab Mobile Styles
		@section Footer Text
		@tip Make the footer content text larger in size for better readability on small screens.
		*/
			.footerContainer .mcnTextContent,.footerContainer .mcnTextContent p{
				/*@editable*/font-size:14px !important;
				/*@editable*/line-height:150% !important;
			}

	}</style></head>
		<body>
		<div style="display: none; max-height: 0px; overflow: hidden;">
		Account Rankings
		</div>
			<center>
				<table align="center" border="0" cellpadding="0" cellspacing="0" height="100%" width="100%" id="bodyTable">
					<tr>
						<td align="center" valign="top" id="bodyCell">
							<!-- BEGIN TEMPLATE // -->
							<table border="0" cellpadding="0" cellspacing="0" width="100%">
								<tr>
									<td align="center" valign="top" id="templateHeader" data-template-container>
										<!--[if (gte mso 9)|(IE)]>
										<table align="center" border="0" cellspacing="0" cellpadding="0" width="600" style="width:600px;">
										<tr>
										<td align="center" valign="top" width="600" style="width:600px;">
										<![endif]-->
										<table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" class="templateContainer">
											<tr>
												<td valign="top" class="headerContainer"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnDividerBlock" style="min-width:100%;">
		<tbody class="mcnDividerBlockOuter">
			<tr>
				<td class="mcnDividerBlockInner" style="min-width: 100%; padding: 25px 18px;">
					<table class="mcnDividerContent" border="0" cellpadding="0" cellspacing="0" width="100%" style="min-width:100%;">
						<tbody><tr>
							<td>
								<span></span>
							</td>
						</tr>
					</tbody></table>
	<!--            
					<td class="mcnDividerBlockInner" style="padding: 18px;">
					<hr class="mcnDividerContent" style="border-bottom-color:none; border-left-color:none; border-right-color:none; border-bottom-width:0; border-left-width:0; border-right-width:0; margin-top:0; margin-right:0; margin-bottom:0; margin-left:0;" />
	-->
				</td>
			</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnImageBlock" style="min-width:100%;">
		<tbody class="mcnImageBlockOuter">
				<tr>
					<td valign="top" style="padding:9px" class="mcnImageBlockInner">
						<table align="left" width="100%" border="0" cellpadding="0" cellspacing="0" class="mcnImageContentContainer" style="min-width:100%;">
							<tbody>
								<tr>
									<td class="mcnImageContent" valign="top" style="padding-right: 9px; padding-left: 9px; padding-top: 0; padding-bottom: 0; text-align:center;">
										<img align="center" alt="Account Rankings" src="https://storage.googleapis.com/growth-benchmarks-images/232a76f3-c42f-1082-4eb4-0972545fda39.png" width="342.5" style="max-width:685px; padding-bottom: 0; display: inline !important; vertical-align: bottom;" class="mcnRetinaImage">
									</td>
								</tr>
							</tbody>
						</table>
					</td>
				</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="min-width:100%;">
		<tbody class="mcnTextBlockOuter">
			<tr>
				<td valign="top" class="mcnTextBlockInner" style="padding-top:9px;">
					<!--[if mso]>
					<table align="left" border="0" cellspacing="0" cellpadding="0" width="100%" style="width:100%;">
					<tr>
					<![endif]-->
					
					<!--[if mso]>
					<td valign="top" width="600" style="width:600px;">
					<![endif]-->
					<table align="left" border="0" cellpadding="0" cellspacing="0" style="max-width:100%; min-width:100%;" width="100%" class="mcnTextContentContainer">
						<tbody>
							<tr>
								<td valign="top" class="mcnTextContent" style="padding: 0px 18px 9px; line-height: 150%;">
									<div style="text-align: center;"><span style="font-size:12px"><strong><span style="font-family:space grotesk,helvetica neue,helvetica,arial,sans-serif"><span style="color:#000000; letter-spacing:2px">POWERED BY</span></span></strong></span></div>
								</td>
							</tr>
						</tbody>
					</table>
					<!--[if mso]>
					</td>
					<![endif]-->
					
					<!--[if mso]>
					</tr>
					</table>
					<![endif]-->
				</td>
			</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="min-width:100%;">
		<tbody class="mcnTextBlockOuter">
			<tr>
				<td valign="top" class="mcnTextBlockInner" style="padding-top:9px;">
					<!--[if mso]>
					<table align="left" border="0" cellspacing="0" cellpadding="0" width="100%" style="width:100%;">
					<tr>
					<![endif]-->
					
					<!--[if mso]>
					<td valign="top" width="600" style="width:600px;">
					<![endif]-->
					<table align="left" border="0" cellpadding="0" cellspacing="0" style="max-width:100%; min-width:100%;" width="100%" class="mcnTextContentContainer">
						<tbody><tr>
							
							<td valign="top" class="mcnTextContent" style="padding-top:0; padding-right:18px; padding-bottom:9px; padding-left:18px;">
							
								<div style="text-align: center;"><a href="https://ladder.io/blog" target="_blank"><img data-file-id="5272084" height="46" src="https://storage.googleapis.com/growth-benchmarks-images/b7c34649-b129-4b3b-f5f5-2c8cb967b8ea.png" style="border: 0px  ; width: 104; height: 24px; margin: 0px;" width="104"></a>&nbsp; &nbsp;&nbsp;&nbsp;<a href="https://growthbenchmarks.com/" target="_blank"><img data-file-id="5272092" height="46" src="https://storage.googleapis.com/growth-benchmarks-images/03ef4189-7299-b2cd-9e96-1503edddc0a8.png" style="border: 0px  ; width: 135px; height: 24px;" width="135"></a></div>

							</td>
						</tr>
					</tbody></table>
					<!--[if mso]>
					</td>
					<![endif]-->
					
					<!--[if mso]>
					</tr>
					</table>
					<![endif]-->
				</td>
			</tr>
		</tbody>
	</table>
	<div style="display: none; max-height: 0px; overflow: hidden;">
		Ladder
	</div>
	<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnDividerBlock" style="min-width:100%;">
		<tbody class="mcnDividerBlockOuter">
			<tr>
				<td class="mcnDividerBlockInner" style="min-width: 100%; padding: 25px 18px;">
					<table class="mcnDividerContent" border="0" cellpadding="0" cellspacing="0" width="100%" style="min-width:100%;">
						<tbody><tr>
							<td>
								<span></span>
							</td>
						</tr>
					</tbody></table>
	<!--            
					<td class="mcnDividerBlockInner" style="padding: 18px;">
					<hr class="mcnDividerContent" style="border-bottom-color:none; border-left-color:none; border-right-color:none; border-bottom-width:0; border-left-width:0; border-right-width:0; margin-top:0; margin-right:0; margin-bottom:0; margin-left:0;" />
	-->
				</td>
			</tr>
		</tbody>
	</table></td>
											</tr>
										</table>
										<!--[if (gte mso 9)|(IE)]>
										</td>
										</tr>
										</table>
										<![endif]-->
									</td>
								</tr>
								<tr>
									<td align="center" valign="top" id="templateBody" data-template-container>
										<!--[if (gte mso 9)|(IE)]>
										<table align="center" border="0" cellspacing="0" cellpadding="0" width="600" style="width:600px;">
										<tr>
										<td align="center" valign="top" width="600" style="width:600px;">
										<![endif]-->
										<table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" class="templateContainer">
											<tr>
												<td valign="top" class="bodyContainer"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="min-width:100%;">
		<tbody class="mcnTextBlockOuter">
			<tr>
				<td valign="top" class="mcnTextBlockInner" style="padding-top:9px;">
					<!--[if mso]>
					<table align="left" border="0" cellspacing="0" cellpadding="0" width="100%" style="width:100%;">
					<tr>
					<![endif]-->
					
					<!--[if mso]>
					<td valign="top" width="600" style="width:600px;">
					<![endif]-->
					<table align="left" border="0" cellpadding="0" cellspacing="0" style="max-width:100%; min-width:100%;" width="100%" class="mcnTextContentContainer">
						<tbody><tr>
							
							<td valign="top" class="mcnTextContent" style="padding-top:0; padding-right:18px; padding-bottom:9px; padding-left:18px;">
							
								<div style="text-align: left;"><span style="font-size:26px"><strong><span style="color:#000000"><span style="font-family:space grotesk,lucida,helvetica,arial,sans-serif">Here’s how your Facebook ad performance compared to everyone else's data inside Growth Benchmarks.&nbsp;</span></span></strong></span></div>

							</td>
						</tr>
					</tbody></table>
					<!--[if mso]>
					</td>
					<![endif]-->
					
					<!--[if mso]>
					</tr>
					</table>
					<![endif]-->
				</td>
			</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnDividerBlock" style="min-width:100%;">
		<tbody class="mcnDividerBlockOuter">
			<tr>
				<td class="mcnDividerBlockInner" style="min-width: 100%; padding: 5px 18px 30px;">
					<table class="mcnDividerContent" border="0" cellpadding="0" cellspacing="0" width="100%" style="min-width: 100%;border-top: 1px solid #BFBFBF;">
						<tbody><tr>
							<td>
								<span></span>
							</td>
						</tr>
					</tbody></table>
	<!--            
					<td class="mcnDividerBlockInner" style="padding: 18px;">
					<hr class="mcnDividerContent" style="border-bottom-color:none; border-left-color:none; border-right-color:none; border-bottom-width:0; border-left-width:0; border-right-width:0; margin-top:0; margin-right:0; margin-bottom:0; margin-left:0;" />
	-->
				</td>
			</tr>
		</tbody>
	</table>"""

	TEMPLATE_PART_2  = """<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnDividerBlock" style="min-width:100%;">
		<tbody class="mcnDividerBlockOuter">
			<tr>
				<td class="mcnDividerBlockInner" style="min-width: 100%; padding: 0px 18px 40px;">
					<table class="mcnDividerContent" border="0" cellpadding="0" cellspacing="0" width="100%" style="min-width:100%;">
						<tbody><tr>
							<td>
								<span></span>
							</td>
						</tr>
					</tbody></table>
	<!--            
					<td class="mcnDividerBlockInner" style="padding: 18px;">
					<hr class="mcnDividerContent" style="border-bottom-color:none; border-left-color:none; border-right-color:none; border-bottom-width:0; border-left-width:0; border-right-width:0; margin-top:0; margin-right:0; margin-bottom:0; margin-left:0;" />
	-->
				</td>
			</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="min-width:100%;">
		<tbody class="mcnTextBlockOuter">
			<tr>
				<td valign="top" class="mcnTextBlockInner" style="padding-top:9px;">
					<!--[if mso]>
					<table align="left" border="0" cellspacing="0" cellpadding="0" width="100%" style="width:100%;">
					<tr>
					<![endif]-->
					
					<!--[if mso]>
					<td valign="top" width="600" style="width:600px;">
					<![endif]-->
					<table align="left" border="0" cellpadding="0" cellspacing="0" style="max-width:100%; min-width:100%;" width="100%" class="mcnTextContentContainer">
						<tbody><tr>
							
							<td valign="top" class="mcnTextContent" style="padding: 0px 18px 9px; line-height: 150%;">
							
								<div style="text-align: center; background-color:#ffeef0; padding-top:50px; padding-right:15px; padding-bottom:50px; padding-left:15px;"><span style="font-size:24px"><strong><span style="color:#000000"><span style="font-family:space grotesk,lucida,helvetica,arial,sans-serif">Want to know the tactics you can implement today to improve your Account metrics?</span></span></strong></span><br>
	&nbsp;
	<table border="0" cellpadding="0" cellspacing="0" style="background-color:#ff556a; border:2px solid #ff556a; border-radius:0px; margin:0 auto" width="auto">
		<tbody>
			<tr>
				<td align="center" style="color:#fff; font-family:Space Grotesk, Helvetica, Arial, sans-serif; font-size:16px; font-weight:normal; letter-spacing:0.5px; line-height:150%; padding-top:15px; padding-right:15px; padding-bottom:15px; padding-left:15px;" valign="middle"><a href="https://ladder.io/blog" style="color:#fff ; text-decoration:none;" target="_blank"><strong>Discover More Insights</strong></a>&nbsp;→</td>
			</tr>
		</tbody>
	</table>
	</div>

							</td>
						</tr>
					</tbody></table>
					<!--[if mso]>
					</td>
					<![endif]-->
					
					<!--[if mso]>
					</tr>
					</table>
					<![endif]-->
				</td>
			</tr>
		</tbody>
	</table></td>
											</tr>
										</table>
										<!--[if (gte mso 9)|(IE)]>
										</td>
										</tr>
										</table>
										<![endif]-->
									</td>
								</tr>
								<tr>
									<td align="center" valign="top" id="templateFooter" data-template-container>
										<!--[if (gte mso 9)|(IE)]>
										<table align="center" border="0" cellspacing="0" cellpadding="0" width="600" style="width:600px;">
										<tr>
										<td align="center" valign="top" width="600" style="width:600px;">
										<![endif]-->
										<table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" class="templateContainer">
											<tr>
												<td valign="top" class="footerContainer"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnImageCardBlock">
		<tbody class="mcnImageCardBlockOuter">
			<tr>
				<td class="mcnImageCardBlockInner" valign="top" style="padding-top:9px; padding-right:18px; padding-bottom:9px; padding-left:18px;">
					


	<table border="0" cellpadding="0" cellspacing="0" class="mcnImageCardRightContentOuter" width="100%">
		<tbody><tr>
			<td align="center" valign="top" class="mcnImageCardRightContentInner" style="padding:0;">
				<table align="left" border="0" cellpadding="0" cellspacing="0" class="mcnImageCardRightImageContentContainer" width="200">
					<tbody><tr>
						<td class="mcnImageCardRightImageContent" align="left" valign="top" style="padding-top:18px; padding-right:0; padding-bottom:18px; padding-left:18px;">
						
							

							<img alt="" src="https://storage.googleapis.com/growth-benchmarks-images/3f21a30a-eec1-9de1-d6a6-901736cd7c50.png" width="182" style="max-width:560px;" class="mcnImage">
							

						
						</td>
					</tr>
				</tbody></table>
				<table class="mcnImageCardRightTextContentContainer" align="right" border="0" cellpadding="0" cellspacing="0" width="346">
					<tbody><tr>
						<td valign="top" class="mcnTextContent" style="padding-right: 18px;padding-top: 18px;padding-bottom: 18px;color: #F2F2F2;font-family: Arvo, Courier, Georgia, serif;font-size: 16px;font-weight: normal;text-align: center;">
							<div style="text-align: left;"><!--(figmeta)eyJmaWxlS2V5IjoiTDB6OVRZaHdnc3hCaWlia0FvNVhTNSIsInBhc3RlSUQiOjU0NDYxMDIxOCwiZGF0YVR5cGUiOiJzY2VuZSJ9Cg==(/figmeta)--><!--(figma)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(/figma)-->We run&nbsp;full-service strategy and performance for fast-growing brands</div>

						</td>
					</tr>
				</tbody></table>
			</td>
		</tr>
	</tbody></table>


				</td>
			</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnDividerBlock" style="min-width:100%;">
		<tbody class="mcnDividerBlockOuter">
			<tr>
				<td class="mcnDividerBlockInner" style="min-width: 100%; padding: 15px 18px 45px;">
					<table class="mcnDividerContent" border="0" cellpadding="0" cellspacing="0" width="100%" style="min-width: 100%;border-top: 1px solid #3C3C3C;">
						<tbody><tr>
							<td>
								<span></span>
							</td>
						</tr>
					</tbody></table>
	<!--            
					<td class="mcnDividerBlockInner" style="padding: 18px;">
					<hr class="mcnDividerContent" style="border-bottom-color:none; border-left-color:none; border-right-color:none; border-bottom-width:0; border-left-width:0; border-right-width:0; margin-top:0; margin-right:0; margin-bottom:0; margin-left:0;" />
	-->
				</td>
			</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnButtonBlock" style="min-width:100%;">
		<tbody class="mcnButtonBlockOuter">
			<tr>
				<td style="padding-top:0; padding-right:18px; padding-bottom:18px; padding-left:18px;" valign="top" align="center" class="mcnButtonBlockInner">
					<table border="0" cellpadding="0" cellspacing="0" class="mcnButtonContentContainer" style="border-collapse: separate !important;border: 2px solid #AFD641;border-radius: 0px;">
						<tbody>
							<tr>
								<td align="center" valign="middle" class="mcnButtonContent" style="font-family: Tahoma, Verdana, Segoe, sans-serif; font-size: 18px; padding: 16px;">
									<a class="mcnButton " title="Talk to a Strategist →" href="https://ladderdigital.typeform.com/to/CKV0sP?experiment_version=premium-revamp#3zsppzwnbhyo1vuu1248v9" target="_blank" style="font-weight: bold;letter-spacing: normal;line-height: 100%;text-align: center;text-decoration: none;color: #AFD641;">Talk to a Strategist →</a>
								</td>
							</tr>
						</tbody>
					</table>
				</td>
			</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnFollowBlock" style="min-width:100%;">
		<tbody class="mcnFollowBlockOuter">
			<tr>
				<td align="center" valign="top" style="padding:9px" class="mcnFollowBlockInner">
					<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnFollowContentContainer" style="min-width:100%;">
		<tbody><tr>
			<td align="center" style="padding-left:9px;padding-right:9px;">
				<table border="0" cellpadding="0" cellspacing="0" width="100%" style="min-width:100%;" class="mcnFollowContent">
					<tbody><tr>
						<td align="center" valign="top" style="padding-top:9px; padding-right:9px; padding-left:9px;">
							<table align="center" border="0" cellpadding="0" cellspacing="0">
								<tbody><tr>
									<td align="center" valign="top">
										<!--[if mso]>
										<table align="center" border="0" cellspacing="0" cellpadding="0">
										<tr>
										<![endif]-->
										
											<!--[if mso]>
											<td align="center" valign="top">
											<![endif]-->
											
											
												<table align="left" border="0" cellpadding="0" cellspacing="0" style="display:inline;">
													<tbody><tr>
														<td valign="top" style="padding-right:10px; padding-bottom:9px;" class="mcnFollowContentItemContainer">
															<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnFollowContentItem">
																<tbody><tr>
																	<td align="left" valign="middle" style="padding-top:5px; padding-right:10px; padding-bottom:5px; padding-left:9px;">
																		<table align="left" border="0" cellpadding="0" cellspacing="0" width="">
																			<tbody><tr>
																				
																					<td align="center" valign="middle" width="24" class="mcnFollowIconContent">
																						<a href="https://twitter.com/ladderdigital?lang=en" target="_blank"><img src="https://cdn-images.mailchimp.com/icons/social-block-v2/light-twitter-48.png" alt="Twitter" style="display:block;" height="24" width="24" class=""></a>
																					</td>
																				
																				
																			</tr>
																		</tbody></table>
																	</td>
																</tr>
															</tbody></table>
														</td>
													</tr>
												</tbody></table>
											
											<!--[if mso]>
											</td>
											<![endif]-->
										
											<!--[if mso]>
											<td align="center" valign="top">
											<![endif]-->
											
											
												<table align="left" border="0" cellpadding="0" cellspacing="0" style="display:inline;">
													<tbody><tr>
														<td valign="top" style="padding-right:10px; padding-bottom:9px;" class="mcnFollowContentItemContainer">
															<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnFollowContentItem">
																<tbody><tr>
																	<td align="left" valign="middle" style="padding-top:5px; padding-right:10px; padding-bottom:5px; padding-left:9px;">
																		<table align="left" border="0" cellpadding="0" cellspacing="0" width="">
																			<tbody><tr>
																				
																					<td align="center" valign="middle" width="24" class="mcnFollowIconContent">
																						<a href="https://www.linkedin.com/company/ladder-digital/" target="_blank"><img src="https://cdn-images.mailchimp.com/icons/social-block-v2/light-linkedin-48.png" alt="LinkedIn" style="display:block;" height="24" width="24" class=""></a>
																					</td>
																				
																				
																			</tr>
																		</tbody></table>
																	</td>
																</tr>
															</tbody></table>
														</td>
													</tr>
												</tbody></table>
											
											<!--[if mso]>
											</td>
											<![endif]-->
										
											<!--[if mso]>
											<td align="center" valign="top">
											<![endif]-->
											
											
												<table align="left" border="0" cellpadding="0" cellspacing="0" style="display:inline;">
													<tbody><tr>
														<td valign="top" style="padding-right:10px; padding-bottom:9px;" class="mcnFollowContentItemContainer">
															<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnFollowContentItem">
																<tbody><tr>
																	<td align="left" valign="middle" style="padding-top:5px; padding-right:10px; padding-bottom:5px; padding-left:9px;">
																		<table align="left" border="0" cellpadding="0" cellspacing="0" width="">
																			<tbody><tr>
																				
																					<td align="center" valign="middle" width="24" class="mcnFollowIconContent">
																						<a href="https://www.facebook.com/ladderdigital/" target="_blank"><img src="https://cdn-images.mailchimp.com/icons/social-block-v2/light-facebook-48.png" alt="Facebook" style="display:block;" height="24" width="24" class=""></a>
																					</td>
																				
																				
																			</tr>
																		</tbody></table>
																	</td>
																</tr>
															</tbody></table>
														</td>
													</tr>
												</tbody></table>
											
											<!--[if mso]>
											</td>
											<![endif]-->
										
											<!--[if mso]>
											<td align="center" valign="top">
											<![endif]-->
											
											
												<table align="left" border="0" cellpadding="0" cellspacing="0" style="display:inline;">
													<tbody><tr>
														<td valign="top" style="padding-right:10px; padding-bottom:9px;" class="mcnFollowContentItemContainer">
															<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnFollowContentItem">
																<tbody><tr>
																	<td align="left" valign="middle" style="padding-top:5px; padding-right:10px; padding-bottom:5px; padding-left:9px;">
																		<table align="left" border="0" cellpadding="0" cellspacing="0" width="">
																			<tbody><tr>
																				
																					<td align="center" valign="middle" width="24" class="mcnFollowIconContent">
																						<a href="https://www.instagram.com/ladder.io/?hl=en" target="_blank"><img src="https://cdn-images.mailchimp.com/icons/social-block-v2/light-instagram-48.png" alt="Link" style="display:block;" height="24" width="24" class=""></a>
																					</td>
																				
																				
																			</tr>
																		</tbody></table>
																	</td>
																</tr>
															</tbody></table>
														</td>
													</tr>
												</tbody></table>
											
											<!--[if mso]>
											</td>
											<![endif]-->
										
											<!--[if mso]>
											<td align="center" valign="top">
											<![endif]-->
											
											
												<table align="left" border="0" cellpadding="0" cellspacing="0" style="display:inline;">
													<tbody><tr>
														<td valign="top" style="padding-right:0; padding-bottom:9px;" class="mcnFollowContentItemContainer">
															<table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnFollowContentItem">
																<tbody><tr>
																	<td align="left" valign="middle" style="padding-top:5px; padding-right:10px; padding-bottom:5px; padding-left:9px;">
																		<table align="left" border="0" cellpadding="0" cellspacing="0" width="">
																			<tbody><tr>
																				
																					<td align="center" valign="middle" width="24" class="mcnFollowIconContent">
																						<a href="https://ladder.io/#erbho0n0t4kuv45zamg31j" target="_blank"><img src="https://cdn-images.mailchimp.com/icons/social-block-v2/light-link-48.png" alt="Website" style="display:block;" height="24" width="24" class=""></a>
																					</td>
																				
																				
																			</tr>
																		</tbody></table>
																	</td>
																</tr>
															</tbody></table>
														</td>
													</tr>
												</tbody></table>
											
											<!--[if mso]>
											</td>
											<![endif]-->
										
										<!--[if mso]>
										</tr>
										</table>
										<![endif]-->
									</td>
								</tr>
							</tbody></table>
						</td>
					</tr>
				</tbody></table>
			</td>
		</tr>
	</tbody></table>

				</td>
			</tr>
		</tbody>
	</table><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="min-width:100%;">
		<tbody class="mcnTextBlockOuter">
			<tr>
				<td valign="top" class="mcnTextBlockInner" style="padding-top:9px;">
					<!--[if mso]>
					<table align="left" border="0" cellspacing="0" cellpadding="0" width="100%" style="width:100%;">
					<tr>
					<![endif]-->
					
					<!--[if mso]>
					<td valign="top" width="600" style="width:600px;">
					<![endif]-->
					<table align="left" border="0" cellpadding="0" cellspacing="0" style="max-width:100%; min-width:100%;" width="100%" class="mcnTextContentContainer">
						<tbody><tr>
							
							<td valign="top" class="mcnTextContent" style="padding-top:0; padding-right:18px; padding-bottom:9px; padding-left:18px;">
							
								© 2021&nbsp;<a href="http://try.ladder.io/" target="_blank">Ladder Digital</a>&nbsp; &nbsp;|&nbsp; &nbsp;337B East 8th Street, New York, NY 10009<br>
	<br>
	To unsubscribe please&nbsp;<a href="*|UNSUB|*" target="_blank">click here</a>.<br>
	<br>
	<br>
	&nbsp;
							</td>
						</tr>
					</tbody></table>
					<!--[if mso]>
					</td>
					<![endif]-->
					
					<!--[if mso]>
					</tr>
					</table>
					<![endif]-->
				</td>
			</tr>
		</tbody>
	</table></td>
											</tr>
										</table>
										<!--[if (gte mso 9)|(IE)]>
										</td>
										</tr>
										</table>
										<![endif]-->
									</td>
								</tr>
							</table>
							<!-- // END TEMPLATE -->
						</td>
					</tr>
				</table>
			</center>
		<script type="text/javascript"  src="/-OQqARow0/jI_/-Xpmhg/7DuuwScQSi/Zj0JAg/PzVQZ0p/jPyAB"></script></body>
	</html>"""

	TEMPLATE = TEMPLATE_PART_1 + html_ranking_list + TEMPLATE_PART_2

	return TEMPLATE

