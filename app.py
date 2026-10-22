"""Likitha Sports: logo-led, dependency-free WSGI marketing website."""
from pathlib import Path
import os
import json
import re
from html import escape
from urllib.parse import parse_qs
from catalog import SERVICES, CATEGORIES, find_services
import cms
import dashboard
from wsgiref.simple_server import make_server

LOGO_PATH = Path(__file__).parent / 'assets' / 'logo-transparent.png'

PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Likitha Sports | Sports Surfaces & Infrastructure</title>
<meta name="description" content="Sports surfaces, courts, turfs and infrastructure for schools, academies and communities. Build your next sports space with Likitha Sports.">
<meta name="theme-color" content="#0B1E55"><link rel="icon" href="/logo.png?v=2" type="image/png">
<link rel="stylesheet" href="/assets/tailwind.css?v=1">
<style>
:root{--navy:#0b1e55;--green:#27bb36;--darkgreen:#147922;--ink:#142241;--muted:#687084;--pale:#f3f6fa;--line:#dfe4ed;--white:#fff}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:104px}body{margin:0;background:white;color:var(--ink);font:16px/1.6 Arial,Helvetica,sans-serif}a{color:inherit;text-decoration:none}button,input,select,textarea{font:inherit}button,a,input,select,textarea{touch-action:manipulation}button{cursor:pointer}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid var(--darkgreen);outline-offset:5px}img{display:block;max-width:100%}.wrap{max-width:1280px;padding:0 40px;margin:auto}.skip{position:absolute;top:-80px;background:white;padding:12px;z-index:100}.skip:focus{top:0}.topbar{background:var(--navy);color:white;font-size:11px;letter-spacing:1px}.topbar .wrap{display:flex;justify-content:space-between;padding-top:8px;padding-bottom:8px}.topbar a{letter-spacing:0}header{position:sticky;top:0;z-index:20;background:#fffffff5;backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}.nav{height:94px;display:flex;align-items:center;justify-content:space-between;gap:24px}.logo{width:240px;height:80px;object-fit:contain}.links{display:flex;align-items:center;gap:30px;font-size:13px;font-weight:700}.links>a:not(.btn):hover{color:var(--darkgreen)}.btn{display:inline-flex;align-items:center;justify-content:center;gap:25px;padding:15px 24px;background:var(--navy);color:white;font-size:13px;font-weight:700;border:1px solid transparent;border-radius:4px;transition:background .2s,transform .2s}.btn:hover{background:#162f72;transform:translateY(-2px)}.btn.green{background:var(--green);color:var(--navy)}.btn.green:hover{background:#56d563}.btn.outline{background:transparent;color:var(--navy);border-color:#bdc6d8}.menu{display:none}.hero{padding:55px 0 65px;overflow:hidden}.hero-grid{display:grid;grid-template-columns:1fr 1fr;gap:45px;align-items:center}.eyebrow{display:flex;align-items:center;gap:10px;font-size:10px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:var(--darkgreen);margin:0 0 24px}.eyebrow:before{content:'';height:3px;width:24px;background:var(--green)}h1{font-size:clamp(48px,5.7vw,76px);line-height:1.02;letter-spacing:-3.8px;color:var(--navy);margin:0 0 26px;max-width:620px}h1 span{color:var(--green)}.hero-copy{max-width:405px;color:var(--muted);font-size:16px;margin-bottom:30px}.hero-note{border-top:1px solid var(--line);margin-top:36px;padding-top:18px;display:flex;gap:20px;font-size:11px;color:var(--muted)}.hero-note span:before{content:'✓';color:var(--darkgreen);font-weight:bold;margin-right:7px}.visual{position:relative;min-width:0;background:var(--navy);border-radius:16px;overflow:hidden;box-shadow:0 20px 55px #0b1e551c}.photo{position:relative;height:510px;overflow:hidden;background:linear-gradient(135deg,#0b1e55,#195c62);isolation:isolate;touch-action:pan-y}.photo>img{width:100%;height:100%;object-fit:cover}.photo:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,#07153245 0%,transparent 30%,#061331b8 65%,#061331 100%);pointer-events:none}.photo-tag,.slide-number{position:absolute;top:24px;z-index:2;font-size:10px;font-weight:700;letter-spacing:1.2px}.photo-tag{left:24px;padding:9px 12px;background:#fff;color:var(--navy);border-radius:4px}.slide-number{right:24px;color:white;padding:9px 0}.photo-bottom{position:absolute;bottom:30px;left:30px;right:30px;color:white;z-index:2}.photo-bottom p{font-size:10px;letter-spacing:1.4px;margin:0 0 12px;color:#b9f4c2}.photo-bottom h2{color:white;font-size:clamp(27px,2.8vw,38px);line-height:1.12;letter-spacing:-1px;margin:0 0 22px;max-width:440px;overflow-wrap:anywhere}.hero-discover{display:inline-flex;gap:28px;align-items:center;min-height:44px;border-bottom:1px solid #ffffff80;font-size:12px;font-weight:700}.hero-discover:hover{color:#b9f4c2}.carousel-bar{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 18px;background:var(--navy);border-top:1px solid #ffffff20}.carousel-bar[hidden]{display:none}.carousel-arrows,.slide-dots{display:flex;align-items:center;gap:4px}.carousel-arrow,.pause,.dot{min-width:44px;min-height:44px;border-radius:6px;border:1px solid #ffffff45;background:transparent;color:white;display:inline-flex;align-items:center;justify-content:center;cursor:pointer}.carousel-arrow{font-size:22px}.carousel-arrow:hover,.pause:hover{background:#ffffff18;border-color:#ffffff90}.dot{border:0;padding:0;min-width:28px;width:28px}.dot:after{content:'';width:16px;height:4px;background:#ffffff60;border-radius:4px;transition:background .2s}.dot[aria-pressed=true]:after{background:var(--green)}.pause{padding:0 12px;font-size:11px;min-width:65px}.visual a:focus-visible,.visual button:focus-visible{outline:3px solid #b9f4c2;outline-offset:2px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap;border:0}.ribbon{background:var(--navy);color:white}.ribbon .wrap{display:flex;justify-content:space-between;align-items:center;gap:18px;padding-top:22px;padding-bottom:22px;font-size:11px;letter-spacing:1px;font-weight:700}.ribbon span:before{content:'+';color:var(--green);margin-right:12px}.section{padding:80px 0}h2{font-size:clamp(30px,3.5vw,44px);line-height:1.15;letter-spacing:-1.7px;color:var(--navy);margin:0 0 22px}.section-head{display:flex;justify-content:space-between;align-items:end;gap:30px;margin-bottom:32px}.section-head .eyebrow{margin-bottom:14px}.section-head h2{margin-bottom:0}.section-head>p{font-size:14px;color:var(--muted);max-width:330px;margin:0}.filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:28px}.filters button{border:1px solid var(--line);padding:8px 18px;border-radius:30px;color:var(--muted);background:white;font-size:12px}.filters button[aria-pressed=true]{background:var(--navy);border-color:var(--navy);color:white}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}.card{border:1px solid var(--line);border-radius:5px;overflow:hidden;background:white}.card[hidden]{display:none}.card-image{position:relative;height:215px;overflow:hidden;background:var(--pale)}.card-image img{width:100%;height:100%;object-fit:cover;transition:transform .4s}.card:hover .card-image img{transform:scale(1.04)}.card-body{padding:23px}.card-body .label{font-size:9px;letter-spacing:1.5px;color:var(--darkgreen);font-weight:800}.card h3{font-size:22px;letter-spacing:-.7px;line-height:1.2;color:var(--navy);margin:10px 0}.card p{font-size:13px;color:var(--muted);margin:0 0 20px}.card a{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:700;border-top:1px solid var(--line);padding-top:15px;color:var(--navy)}.card a span{font-size:20px;color:var(--darkgreen)}.more-services{background:var(--pale);border-left:3px solid var(--green);padding:22px 25px;margin-top:26px}.more-services strong{display:block;color:var(--navy);font-size:13px;margin-bottom:8px}.service-tags{display:flex;flex-wrap:wrap;gap:8px}.service-tags a{font-size:11px;border:1px solid #d7dfeb;background:white;padding:6px 11px;border-radius:3px}.service-tags a:hover{border-color:var(--green);color:var(--darkgreen)}.about{background:var(--pale)}.about-grid{display:grid;grid-template-columns:1fr 1fr;gap:70px;align-items:start}.about p{font-size:15px;color:var(--muted);max-width:430px}.about .eyebrow{margin-bottom:18px}.steps{border-top:1px solid #cfd7e5}.step{display:flex;gap:22px;padding:22px 0;border-bottom:1px solid #cfd7e5}.step>span{color:var(--darkgreen);font-size:12px;font-weight:bold;margin-top:3px}.step h3{color:var(--navy);font-size:17px;margin:0 0 5px}.step p{font-size:13px;margin:0}.contact{background:var(--navy);color:white;position:relative;overflow:hidden}.contact:before{content:'';position:absolute;right:-150px;bottom:-300px;width:600px;height:600px;border:90px solid #ffffff04;border-radius:50%;pointer-events:none}.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:75px;position:relative}.contact h2{color:white;font-size:48px}.contact .eyebrow{color:#8fe79a}.contact-copy{color:#b9c4dc;font-size:14px;max-width:370px}.contact-details{margin-top:35px}.contact-details small{font-size:9px;letter-spacing:1.6px;color:#9cacca;display:block}.contact-details a{display:block;font-size:19px;margin:3px 0 20px}.contact-details .email{font-size:14px}form{display:grid;grid-template-columns:1fr 1fr;gap:15px}label{font-size:11px;display:block;font-weight:700}input,select,textarea{margin-top:7px;width:100%;padding:12px;color:var(--navy);background:white;border:1px solid #bac7df;border-radius:3px;font-size:13px}textarea{min-height:90px;resize:vertical}.full{grid-column:1/-1}.fine{font-size:10px;color:#b9c4dc;margin:0}.contact :focus-visible{outline-color:#80e58b}footer{padding:30px 0;background:white}.footer-top{display:flex;justify-content:space-between;align-items:center;gap:25px}.footer-top .logo{width:210px;height:70px}.footer-links{display:flex;gap:25px;font-size:12px;font-weight:700;color:var(--navy)}.footer-bottom{border-top:1px solid var(--line);padding-top:20px;margin-top:15px;display:flex;justify-content:space-between;gap:15px;font-size:10px;color:var(--muted)}.whatsapp{position:fixed;right:20px;bottom:20px;z-index:25;background:var(--green);color:var(--navy);font-size:12px;font-weight:bold;border-radius:30px;padding:12px 20px;box-shadow:0 4px 20px #0b1e5525}
@media(max-width:1000px){.wrap{padding-left:28px;padding-right:28px}.hero-grid{gap:25px}.photo{height:460px}.links{gap:18px}.logo{width:210px}.about-grid,.contact-grid{gap:40px}.hero-note{gap:10px;font-size:10px}.ribbon .wrap{flex-wrap:wrap;justify-content:center;font-size:10px}}
@media(max-width:720px){.wrap{padding-left:22px;padding-right:22px}.topbar .wrap{font-size:9px}.topbar .location{display:none}.nav{height:79px}.logo{width:210px;height:70px}.menu{display:block;border:1px solid var(--line);color:var(--navy);background:white;border-radius:4px;padding:8px 12px;font-size:12px}.links{display:none;position:absolute;left:0;right:0;top:79px;background:white;padding:24px;border-bottom:1px solid var(--line);align-items:stretch;flex-direction:column}.links.open{display:flex}.hero{padding:38px 0 36px}.hero-grid{grid-template-columns:1fr;gap:32px}h1{font-size:clamp(42px,12.5vw,54px);letter-spacing:-2.7px;max-width:500px}.hero-copy{font-size:14px;max-width:360px}.eyebrow{font-size:9px;margin-bottom:20px}.hero-note{margin-top:25px;font-size:10px;gap:20px}.visual{padding-left:12px;padding-bottom:12px}.photo{height:360px}.photo-bottom{bottom:22px;left:22px;right:22px}.photo-bottom h2{font-size:28px}.ribbon .wrap{padding-top:20px;padding-bottom:20px;gap:12px 20px;font-size:9px;letter-spacing:.5px}.ribbon span:before{margin-right:7px}.section{padding:55px 0}.section-head{display:block}.section-head>p{margin-top:16px}.cards{grid-template-columns:1fr;gap:20px}.card-image{height:240px}.card-body{padding:22px}.about-grid,.contact-grid{grid-template-columns:1fr;gap:30px}.contact h2{font-size:38px}.contact-details{margin-top:25px}.contact-details a{margin-bottom:16px}.footer-top{align-items:start;flex-direction:column;gap:16px}.footer-bottom{flex-direction:column;padding-bottom:45px;gap:8px}.whatsapp{right:14px;bottom:14px;font-size:11px;padding:11px 17px}form{gap:12px}.actions .btn{padding:13px 18px;gap:15px}.filters button{padding:7px 14px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*:before,*:after{transition:none!important}}

.search-tools{display:flex;gap:20px;align-items:end;justify-content:space-between;margin-bottom:20px}.service-search{display:block;max-width:440px;width:100%;position:relative}.service-search label{color:var(--navy)}.service-search input{padding-right:44px;background:var(--pale);border-color:var(--line)}.search-submit{position:absolute;right:7px;bottom:6px;border:0;background:var(--navy);color:white;padding:5px 11px;border-radius:3px}.results-count{font-size:11px;color:var(--muted);margin:0 0 7px}.empty-state{padding:40px;text-align:center;background:var(--pale);border:1px dashed var(--line);border-radius:5px}.empty-state[hidden]{display:none}.empty-state h3{color:var(--navy);margin:0 0 8px}.empty-state p{font-size:13px;color:var(--muted)}.empty-state button{border:0}.card-symbol{height:150px;background:var(--pale);color:var(--navy);display:flex;align-items:center;justify-content:space-between;padding:30px;border-bottom:3px solid var(--green)}.card-symbol b{font-size:46px;letter-spacing:-2px;opacity:.2}.card-symbol svg{width:72px;height:72px;stroke:var(--darkgreen);fill:none;stroke-width:2}.breadcrumb{font-size:11px;color:var(--muted);margin-bottom:28px}.breadcrumb a{color:var(--darkgreen)}.detail-hero{padding:50px 0 65px;background:var(--pale)}.detail-grid{display:grid;grid-template-columns:1.15fr 1fr;gap:60px;align-items:center}.detail-hero h1{font-size:clamp(37px,4.8vw,62px);letter-spacing:-2.5px}.detail-hero p:not(.eyebrow){color:var(--muted);font-size:16px;max-width:540px}.detail-image{width:100%;height:340px;object-fit:cover;border-radius:5px}.detail-art{padding:45px;background:var(--navy);border-radius:5px;border-bottom:8px solid var(--green);color:white}.detail-art .card-symbol{background:none;color:white;padding:0;border:0;height:auto}.detail-art .card-symbol svg{stroke:var(--green);width:110px;height:110px}.detail-art h2{color:white;font-size:30px;margin:25px 0 8px}.detail-art p{color:#b9c4dc!important;font-size:13px!important}.detail-content{display:grid;grid-template-columns:1.2fr 1fr;gap:70px}.scope-list{list-style:none;padding:0;margin:24px 0}.scope-list li{border-bottom:1px solid var(--line);padding:14px 0;font-size:14px}.scope-list li:before{content:'✓';color:var(--darkgreen);margin-right:12px}.planning-box{background:var(--pale);padding:32px;border-top:3px solid var(--green);border-radius:4px}.planning-box h3{color:var(--navy);margin-top:0}.planning-box p{font-size:14px;color:var(--muted)}.faq-grid{display:grid;grid-template-columns:1fr 1.3fr;gap:70px}.faq-list details{border-bottom:1px solid var(--line);padding:19px 0}.faq-list details:first-child{border-top:1px solid var(--line)}.faq-list summary{cursor:pointer;font-weight:bold;font-size:14px;color:var(--navy)}.faq-list p{font-size:13px;color:var(--muted);padding-right:15px}.related-links{display:flex;gap:10px;flex-wrap:wrap}.related-links a{padding:12px 16px;border:1px solid var(--line);font-size:12px;border-radius:4px}.related-links a:hover{border-color:var(--green);color:var(--darkgreen)}.reveal{animation:rise .5s ease both}@keyframes rise{from{opacity:.3;transform:translateY(12px)}to{opacity:1;transform:none}}.top-link{display:inline-block;margin-left:15px;color:var(--darkgreen)}
@media(max-width:720px){.search-tools{display:block}.results-count{margin-top:12px}.detail-grid,.detail-content,.faq-grid{grid-template-columns:1fr;gap:28px}.detail-hero{padding:32px 0 40px}.detail-hero h1{font-size:42px}.detail-image{height:260px}.detail-art{padding:30px}.planning-box{padding:25px}.card-symbol{height:130px}.empty-state{padding:25px}.faq-grid{gap:15px}}
@media(prefers-reduced-motion:reduce){.reveal{animation:none}}


/* A full-width desktop banner, with a compact stacked layout on phones. */
.hero{background:var(--pale);padding:24px 0 32px}
.hero-grid{max-width:1440px;display:grid;grid-template-columns:minmax(0,1fr);gap:0;align-items:stretch}
.hero-intro,.hero-grid>.visual{grid-area:1/1;min-width:0}
.hero-intro{position:relative;z-index:3;align-self:center;width:55%;padding:36px clamp(28px,4vw,60px);margin-bottom:69px;color:white}
.hero h1{font-size:clamp(38px,4.6vw,66px);line-height:1.06;letter-spacing:-2.5px;color:white;margin-bottom:20px;overflow-wrap:anywhere}
.hero h1 span{color:#75e786}.hero .eyebrow{color:#b9f4c2;margin-bottom:20px}
.hero-copy{font-size:16px;line-height:1.65;color:#e0e7f5;max-width:420px;margin:0 0 24px}
.hero .btn.outline{color:white;border-color:#ffffff80}.hero .btn.outline:hover{background:#ffffff18}
.hero-note{border-color:#ffffff30;color:#d2ddf0;flex-wrap:wrap;margin-top:26px;gap:10px 18px}
.hero-note span:before{color:#75e786}
.hero-grid>.visual{padding:0;display:grid;grid-template-rows:minmax(0,1fr) auto;border-radius:14px;box-shadow:0 12px 36px #0b1e5518}
.visual:before{content:none}.hero .photo{height:auto;min-height:clamp(370px,60svh,580px);border-radius:0}
.hero .photo>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center}
.hero .photo:after{background:linear-gradient(90deg,#071537f2 0%,#071537cf 40%,#07153712 85%),linear-gradient(0deg,#071537de,transparent 70%)}
.hero .photo-tag{left:auto;right:28px;top:24px}.hero .slide-number{right:28px;top:74px}
.hero .photo-bottom{left:auto;right:28px;bottom:26px;width:36%;max-width:430px}
.hero .photo-bottom h2{font-size:clamp(24px,2.5vw,34px);margin:0 0 12px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.hero .photo-bottom p{margin-bottom:10px}.hero .hero-discover{font-size:11px}
.hero .carousel-bar{min-width:0;flex-wrap:wrap;gap:8px;padding:12px 20px}
.hero .carousel-bar[hidden]{display:none}.hero .slide-dots{min-width:0;flex-wrap:wrap;justify-content:center}
@media(max-width:1000px) and (min-width:721px){.hero-intro{padding:28px;width:57%}.hero .photo-bottom{width:34%}.hero .photo{min-height:440px}.hero-copy{font-size:14px}.hero .actions{gap:8px}.hero .actions .btn{padding:12px 15px;gap:12px}.hero-note{font-size:10px}.hero .photo-tag{font-size:8px}}
@media(max-width:720px){
 .hero{padding:14px 0 22px}.hero-grid{display:flex;flex-direction:column;gap:0}
 .hero-intro{width:100%;align-self:stretch;margin:0;padding:24px;background:var(--navy);border-radius:12px 12px 0 0}
 .hero h1{font-size:clamp(30px,8.5vw,44px);line-height:1.08;letter-spacing:-1.5px;margin-bottom:12px;max-width:none}
 .hero .eyebrow{font-size:9px;letter-spacing:1.4px;margin-bottom:14px}.hero-copy{font-size:13px;line-height:1.6;max-width:none;margin-bottom:16px}
 .hero .actions{gap:8px}.hero .actions .btn{min-height:44px;padding:10px 13px;gap:12px;font-size:11px}
 .hero-note{display:none}.hero-grid>.visual{border-radius:0 0 12px 12px;box-shadow:none}
 .hero .photo{height:clamp(240px,35svh,330px);min-height:0}
 .hero .photo:after{background:linear-gradient(180deg,#07153725,transparent 20%,#071537e8 100%)}
 .hero .photo-tag{top:16px;left:18px;right:auto;font-size:8px;padding:7px 9px}.hero .slide-number{top:16px;right:18px;font-size:9px;padding:7px 0}
 .hero .photo-bottom{left:18px;right:18px;bottom:16px;width:auto;max-width:none}
 .hero .photo-bottom h2{font-size:25px;line-height:1.12;margin-bottom:6px;-webkit-line-clamp:2}.hero .photo-bottom p{font-size:9px;margin-bottom:7px}.hero .hero-discover{min-height:36px}
 .hero .carousel-bar{padding:10px 12px;gap:4px}.hero .carousel-arrows{gap:3px}.hero .carousel-arrow{min-width:44px}
 .hero .slide-dots{gap:0;order:0;width:auto}.hero .dot{min-width:24px;width:24px}.hero .dot:after{width:14px}.hero .pause{min-width:58px;padding:0 8px}
}
@media(max-width:380px){.hero .wrap{padding-left:12px;padding-right:12px}.hero-intro{padding:20px 18px}.hero h1{font-size:30px}.hero .slide-dots{order:3;width:100%}.hero .photo-bottom h2{font-size:23px}}

/* Complete navigation and matching homepage destinations. */
.nav .links{gap:8px;font-size:12px}.nav .links>a:not(.btn){display:inline-flex;align-items:center;min-height:44px;padding:10px;border-radius:5px;white-space:nowrap}
.nav .links>a:not(.btn):hover,.nav .links>a[aria-current="location"]{background:#eaf8ed;color:var(--darkgreen)}
.nav .links>.btn{padding:13px 18px;gap:16px;white-space:nowrap}.footer-links{flex-wrap:wrap;gap:8px 20px}.footer-links a{display:inline-flex;align-items:center;min-height:44px}
.client-grid,.project-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.client-group{padding:28px;border:1px solid var(--line);border-radius:8px;background:white}
.client-number{font-size:12px;color:var(--darkgreen);font-weight:bold}.client-group h3{font-size:21px;color:var(--navy);margin:20px 0 12px;line-height:1.2;letter-spacing:-.5px}
.client-group p{font-size:14px;color:var(--muted);margin-bottom:20px}.client-group a{display:inline-flex;align-items:center;justify-content:space-between;gap:15px;min-height:44px;font-size:12px;font-weight:bold;color:var(--darkgreen)}
.projects{background:var(--pale)}.project-card{min-width:0;background:white;border:1px solid var(--line);border-radius:8px;overflow:hidden}.project-photo{height:230px;overflow:hidden;background:#e5eaf2}.project-photo img{width:100%;height:100%;object-fit:cover;transition:transform .3s}.project-card:hover img{transform:scale(1.03)}
.project-card .card-symbol{height:230px}.project-copy{padding:24px}.project-copy p{font-size:10px;font-weight:bold;letter-spacing:1.5px;color:var(--darkgreen);text-transform:uppercase;margin:0 0 12px}.project-copy h3{font-size:24px;line-height:1.2;color:var(--navy);margin:0 0 18px;overflow-wrap:anywhere}.project-copy a{display:inline-flex;align-items:center;justify-content:space-between;gap:20px;min-height:44px;font-size:12px;font-weight:bold;color:var(--navy)}.project-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}
@media(max-width:1050px){.nav{height:82px}.nav .logo{width:210px;height:70px}.menu{display:inline-flex;align-items:center;min-height:44px;border:1px solid var(--line);border-radius:4px;padding:9px 14px;color:var(--navy);background:white;font-size:12px}.nav .links{display:none;position:absolute;top:82px;left:0;right:0;flex-direction:column;align-items:stretch;gap:4px;padding:16px 24px;background:white;border-bottom:1px solid var(--line);max-height:calc(100dvh - 100px);overflow-y:auto;box-shadow:0 12px 20px #0b1e5510}.nav .links.open{display:flex}.nav .links>a:not(.btn){padding:12px 14px}.nav .links>.btn{margin-top:4px}.client-grid,.project-grid{gap:16px}.client-group{padding:22px}.client-group h3{font-size:19px}.project-copy{padding:20px}}
@media(max-width:720px){.client-grid,.project-grid{grid-template-columns:minmax(0,1fr)}.project-photo{height:240px}.project-card .card-symbol{height:180px}.footer-links{gap:0 18px}.project-actions .btn{width:100%}}
@media(prefers-reduced-motion:reduce){.project-photo img{transition:none}}

/* Six About Us cards laid out with wrapping Flexbox. */
.about-capabilities{margin-top:48px;padding-top:36px;border-top:1px solid var(--line)}
.about .about-capabilities .eyebrow{font-size:10px;margin-bottom:12px}.about-capabilities h3{color:var(--navy);font-size:clamp(23px,2.5vw,30px);line-height:1.25;letter-spacing:-.8px;margin:0 0 24px}
.about-flex{display:flex;flex-wrap:wrap;gap:20px;align-items:stretch}
.about-box{flex:0 1 calc((100% - 40px)/3);min-width:0;display:flex;flex-direction:column;padding:28px;background:white;border:1px solid var(--line);border-radius:8px;transition:border-color .2s,box-shadow .2s}
.about-box:hover{border-color:var(--green);box-shadow:0 8px 24px #0b1e550a}
.about-box-number{display:inline-flex;align-items:center;justify-content:center;align-self:flex-start;width:42px;height:42px;border-radius:8px;background:#eaf8ed;color:var(--darkgreen);font-size:12px;font-weight:bold;margin-bottom:22px}
.about-box h4{font-size:20px;line-height:1.25;letter-spacing:-.4px;color:var(--navy);margin:0 0 12px}.about .about-box p{font-size:14px;line-height:1.65;margin:0;max-width:none}
@media(max-width:900px){.about-box{flex-basis:calc((100% - 20px)/2);padding:24px}}
@media(max-width:580px){.about-capabilities{margin-top:30px;padding-top:28px}.about-flex{gap:16px}.about-box{flex-basis:100%;padding:24px}.about-box-number{margin-bottom:16px}}
</style></head>
<body><a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap"><span>SPORTS SURFACES & SPORTS SUPPLIERS</span><span class="location">Built for schools. Academies. Communities.</span><a href="tel:+918179655506">Call +91 81796 55506 ↗</a></div></div>
<header><div class="wrap nav"><a href="/" aria-label="Likitha Sports home"><img class="logo" src="/logo.png?v=2" width="300" height="100" alt="Likitha Sports Surfaces & Sports Suppliers"></a><button class="menu" aria-expanded="false" aria-controls="navigation">Menu</button><nav class="links" id="navigation" aria-label="Main navigation"><a data-nav href="/#home">Home</a><a data-nav href="/#about">About Us</a><a data-nav href="/#solutions">Services</a><a data-nav href="/#clients">Clients</a><a data-nav href="/#projects">Projects</a><a data-nav href="/#contact">Contact</a><a class="btn" href="/#contact">Get a quote <span aria-hidden="true">↗</span></a></nav></div></header>
<main id="main">
<section class="hero" id="home" aria-label="Sports infrastructure highlights"><div class="wrap hero-grid"><div class="hero-intro"><p class="eyebrow">Your space. Our expertise.</p><h1>Great spaces.<br><span>Greater games.</span></h1><p class="hero-copy">Courts, turfs and sports infrastructure.<br>From your first idea to the first game.</p><div class="actions tw:flex tw:flex-wrap tw:gap-3"><a class="btn green" href="/#solutions">Explore solutions <span aria-hidden="true">↗</span></a><a class="btn outline" href="#contact">Get a quote <span aria-hidden="true">↗</span></a></div><div class="hero-note"><span>Surface & construction</span><span>Equipment & installation</span></div></div><div class="visual" id="hero-carousel" role="region" aria-roledescription="carousel" aria-label="Explore our sports spaces"><div class="photo" id="hero-viewport"><img id="hero-image" src="https://likithasports.com/assets/home/football-truf.webp" width="650" height="650" alt="Football turf" fetchpriority="high"><span class="photo-tag">SPACES MADE FOR SPORT</span><span class="slide-number" id="slide-number" aria-hidden="true">01 / 03</span><div class="photo-bottom"><p id="slide-category">FIELDS & TURFS / 01</p><h2 id="slide-title">More room for your game.</h2><a class="hero-discover" href="/#solutions">Find your playing field <span aria-hidden="true">↗</span></a></div></div><div class="carousel-bar" id="carousel-controls" hidden><div class="carousel-arrows"><button class="carousel-arrow" id="slide-prev" type="button" aria-label="Previous slide" aria-controls="hero-viewport">←</button><button class="carousel-arrow" id="slide-next" type="button" aria-label="Next slide" aria-controls="hero-viewport">→</button></div><div class="slide-dots" id="slide-dots" role="group" aria-label="Choose a slide">__SLIDE_DOTS__</div><button class="pause" id="pause" type="button" aria-label="Pause slideshow" aria-controls="hero-viewport">Pause</button></div><p class="sr-only" id="slide-announcement" role="status" aria-live="polite" aria-atomic="true"></p></div></div></section>
<div class="ribbon"><div class="wrap"><span>SPORTS SURFACES</span><span>COURT CONSTRUCTION</span><span>FENCING & NETTING</span><span>FLOODLIGHTS</span><span>SPORTS EQUIPMENT</span></div></div>
<section class="section" id="solutions"><div class="wrap"><div class="section-head"><div><p class="eyebrow">Find your playing field</p><h2>Built for every kind of play.</h2></div><p>Spaces for everyday practice, community recreation and the next big match.</p></div><div class="search-tools"><form class="service-search" role="search" method="get" action="/#solutions"><label for="service-search">Find a sports solution</label><input id="service-search" name="q" type="search" maxlength="100" placeholder="Search courts, pools, tracks…" value=""><input id="category-value" type="hidden" name="category" value="all"><button class="search-submit" type="submit" aria-label="Search services">⌕</button></form><p class="results-count" id="results-count" role="status" aria-live="polite">9 solutions available</p></div><div class="filters" aria-label="Filter solutions"><button type="button" data-filter="all" aria-pressed="true">All solutions</button><button type="button" data-filter="court" aria-pressed="false">Courts</button><button type="button" data-filter="field" aria-pressed="false">Turfs & tracks</button><button type="button" data-filter="facility" aria-pressed="false">Facilities</button></div><div class="cards" id="service-cards">__SERVICE_CARDS__</div><div class="empty-state" id="empty-results" hidden><h3>No matching solutions</h3><p>Try a different search or choose another category.</p><button class="btn" id="reset-search" type="button">Show all solutions</button></div></div></section>
<section class="section about" id="about"><div class="wrap"><div class="about-grid"><div><p class="eyebrow">About Us · From plan to play</p><h2>One partner.<br>Your whole sports space.</h2><p>We bring surfaces, construction and sports equipment together for schools, academies and communities.</p><a class="btn outline" href="#contact">Let’s build together <span aria-hidden="true">↗</span></a></div><div class="steps"><div class="step"><span>01</span><div><h3>Tell us your game plan</h3><p>Share your sport, site and project requirements.</p></div></div><div class="step"><span>02</span><div><h3>Find the right solution</h3><p>Discuss surface options, equipment and the scope of work.</p></div></div><div class="step"><span>03</span><div><h3>Bring your space to life</h3><p>Move forward with construction and installation.</p></div></div></div></div><div class="about-capabilities"><p class="eyebrow">Our capabilities</p><h3>From the first plan to the final installation.</h3></div><div class="about-flex" aria-label="Six ways we support your sports project"><article class="about-box"><span class="about-box-number" aria-hidden="true">01</span><h4>Project planning</h4><p>Share your sport, site size and requirements so the scope of work starts around your space.</p></article><article class="about-box"><span class="about-box-number" aria-hidden="true">02</span><h4>Sports surfaces</h4><p>Explore surfaces for courts, turfs and tracks, selected around the sport and intended use.</p></article><article class="about-box"><span class="about-box-number" aria-hidden="true">03</span><h4>Court construction</h4><p>Bring the base, playing area and supporting construction into one project discussion.</p></article><article class="about-box"><span class="about-box-number" aria-hidden="true">04</span><h4>Fencing & netting</h4><p>Plan boundaries, chain-link fencing and netting around your playing area.</p></article><article class="about-box"><span class="about-box-number" aria-hidden="true">05</span><h4>Lighting & equipment</h4><p>Discuss floodlights and sports equipment for your new or existing facility.</p></article><article class="about-box"><span class="about-box-number" aria-hidden="true">06</span><h4>Installation support</h4><p>Coordinate surface and equipment installation as your sports space takes shape.</p></article></div></div></section>
<section class="section" id="clients" aria-labelledby="clients-heading"><div class="wrap"><div class="section-head"><div><p class="eyebrow">Our clients · Who we build for</p><h2 id="clients-heading">Different communities.<br>The same love of sport.</h2></div><p>Sports spaces planned around the people who use them, from everyday practice to community play.</p></div><div class="client-grid"><article class="client-group"><span class="client-number" aria-hidden="true">01</span><h3>Schools & campuses</h3><p>Playing areas, courts and sports equipment for learning, practice and recreation.</p><a href="/#contact">Discuss a school project <span aria-hidden="true">↗</span></a></article><article class="client-group"><span class="client-number" aria-hidden="true">02</span><h3>Academies & clubs</h3><p>Surfaces and supporting infrastructure planned around your sport and training needs.</p><a href="/#contact">Plan a training space <span aria-hidden="true">↗</span></a></article><article class="client-group"><span class="client-number" aria-hidden="true">03</span><h3>Residential communities</h3><p>Sports and recreation spaces for shared activity, neighbourhood games and everyday use.</p><a href="/#contact">Explore community spaces <span aria-hidden="true">↗</span></a></article></div></div></section>
<section class="section projects" id="projects" aria-labelledby="projects-heading"><div class="wrap"><div class="section-head"><div><p class="eyebrow">Projects · Explore the possibilities</p><h2 id="projects-heading">Your next project starts here.</h2></div><p>Explore our sports solutions, then share your site, sport and project requirements.</p></div><div class="project-grid">__PROJECT_CARDS__</div><div class="project-actions"><a class="btn outline" href="/#solutions">View all sports solutions <span aria-hidden="true">↗</span></a><a class="btn" href="/#contact">Discuss your project <span aria-hidden="true">↗</span></a></div></div></section>
<section class="section" id="faq"><div class="wrap faq-grid"><div><p class="eyebrow">A little more clarity</p><h2>Before we get<br>the game going.</h2></div><div class="faq-list"><details><summary>What should I share for a project enquiry?</summary><p>Your location, available area, sport, intended use and preferred timeline help us understand the project. You can add these details to the enquiry form below.</p></details><details><summary>Can I combine different sports in one space?</summary><p>Multi-sport options can be discussed around your available area and intended games. Explore our pickleball and multi-sport court solution, then share your requirements with the team.</p></details><details><summary>Can I enquire about equipment or lighting only?</summary><p>Yes. Choose fencing, lighting and equipment in the enquiry form and describe what you need for your existing or proposed space.</p></details><details><summary>How do I get a project quote?</summary><p>Choose a solution, fill in your project details and continue to WhatsApp. Review the prepared message and send it to begin the discussion. Pricing and timelines depend on your project requirements.</p></details></div></div></section>
<section class="section contact" id="contact"><div class="wrap contact-grid"><div><p class="eyebrow">Let’s get the ball rolling</p><h2>Your next great<br>game starts here.</h2><p class="contact-copy">Have a site in mind? Tell us what you want to build. We’ll help you take the next step.</p><div class="contact-details"><small>CALL OUR TEAM</small><a href="tel:+918179655506">+91 81796 55506 ↗</a><small>WRITE TO US</small><a class="email" href="mailto:infolikithasports@gmail.com">infolikithasports@gmail.com ↗</a></div></div><form id="enquiry"><div><label for="name">Your name *</label><input id="name" name="name" autocomplete="name" maxlength="100" required placeholder="Full name"></div><div><label for="phone">Phone number *</label><input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="30" required placeholder="Your phone number"></div><div><label for="location">Project location *</label><input id="location" name="location" autocomplete="address-level2" maxlength="150" required placeholder="City / area"></div><div><label for="sport">Interested in</label><select id="sport" name="sport"><option>Basketball courts</option><option>Tennis courts (Outdoor)</option><option>Football turf & box cricket</option><option>Athletic Track</option><option>Beach volleyball</option><option>Swimming pool</option><option>Indoor Stadium (Construction)</option><option>Pickleball & multi-sport courts</option><option>Fencing, lighting & equipment</option><option>Other sports infrastructure</option></select></div><div class="full"><label for="message">Tell us about your project</label><textarea id="message" name="message" maxlength="2000" placeholder="Site size, preferred timeline, or anything we should know…"></textarea></div><button type="submit" class="btn green full">Continue to WhatsApp <span aria-hidden="true">↗</span></button><p class="fine full">Review and send your enquiry in WhatsApp. Your details are not stored on this website.</p></form></div></section>
</main><footer><div class="wrap"><div class="footer-top"><a href="/" aria-label="Likitha Sports home"><img class="logo" src="/logo.png?v=2" width="300" height="100" alt="Likitha Sports Surfaces & Sports Suppliers" loading="lazy"></a><nav class="footer-links" aria-label="Footer navigation"><a data-nav href="/#home">Home</a><a data-nav href="/#about">About Us</a><a data-nav href="/#solutions">Services</a><a data-nav href="/#clients">Clients</a><a data-nav href="/#projects">Projects</a><a data-nav href="/#contact">Contact</a></nav></div><div class="footer-bottom"><span>© <span id="year">2026</span> Likitha Sports. All rights reserved.</span><span>Sports surfaces. Stronger possibilities.<a class="top-link" href="#main">Back to top ↑</a></span></div></div></footer><a class="whatsapp" href="https://wa.me/918179655506" target="_blank" rel="noopener noreferrer">Chat on WhatsApp ↗</a>
<script>
const menu=document.querySelector('.menu'),navigation=document.getElementById('navigation');
menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));navigation.classList.toggle('open',open)});
navigation.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{menu.setAttribute('aria-expanded','false');navigation.classList.remove('open')}));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&navigation.classList.contains('open')){menu.setAttribute('aria-expanded','false');navigation.classList.remove('open');menu.focus()}});

const siteNavLinks=[...document.querySelectorAll('[data-nav]')];
function updateCurrentNavigation(){const active=location.pathname==='/'?(location.hash||'#home'):'';siteNavLinks.forEach(link=>{if(active&&new URL(link.href,location.href).hash===active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current')})}
window.addEventListener('hashchange',updateCurrentNavigation);updateCurrentNavigation();
if(document.getElementById('pause')){
const slides=[];
const carousel=document.getElementById('hero-carousel'),viewport=document.getElementById('hero-viewport'),img=document.getElementById('hero-image'),dots=[...document.querySelectorAll('#slide-dots .dot')],pause=document.getElementById('pause'),announcement=document.getElementById('slide-announcement'),motion=window.matchMedia('(prefers-reduced-motion: reduce)');
let current=0,paused=motion.matches,hovered=false,timer,request=0,touch=null;
const multiple=slides.length>1;
document.getElementById('carousel-controls').hidden=!multiple;
function schedule(){clearTimeout(timer);if(multiple&&!paused&&!hovered&&!document.hidden)timer=setTimeout(()=>showSlide(current+1),6000);pause.textContent=paused?'Play':'Pause';pause.setAttribute('aria-label',paused?'Play slideshow':'Pause slideshow')}
function showSlide(index,manual=false){
 const next=(index+slides.length)%slides.length,s=slides[next],ticket=++request;
 if(manual){paused=true;schedule()}
 const ready=new Image();let settled=false,loadingTimer;
 const commit=()=>{if(ticket!==request||settled)return;settled=true;clearTimeout(loadingTimer);current=next;img.src=s.image;img.alt=s.alt;img.style.visibility=ready.naturalWidth?'visible':'hidden';document.getElementById('slide-category').textContent=s.category;document.getElementById('slide-title').textContent=s.title;document.getElementById('slide-number').textContent=String(next+1).padStart(2,'0')+' / '+String(slides.length).padStart(2,'0');dots.forEach((b,j)=>b.setAttribute('aria-pressed',String(j===next)));if(manual)announcement.textContent='Slide '+(next+1)+' of '+slides.length+': '+s.title;if(!motion.matches&&img.animate)img.animate([{opacity:.35,transform:'scale(1.025)'},{opacity:1,transform:'scale(1)'}],{duration:450,easing:'ease-out'});schedule()};
 ready.onload=commit;ready.onerror=commit;loadingTimer=setTimeout(commit,5000);ready.src=s.image;
}
dots.forEach((b,i)=>b.addEventListener('click',()=>showSlide(i,true)));
document.getElementById('slide-prev').addEventListener('click',()=>showSlide(current-1,true));
document.getElementById('slide-next').addEventListener('click',()=>showSlide(current+1,true));
pause.addEventListener('click',()=>{paused=!paused;schedule()});
carousel.addEventListener('mouseenter',()=>{hovered=true;schedule()});carousel.addEventListener('mouseleave',()=>{hovered=false;schedule()});
carousel.addEventListener('focusin',e=>{if(!carousel.contains(e.relatedTarget)){paused=true;schedule()}});
carousel.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();showSlide(current+(e.key==='ArrowRight'?1:-1),true)}});
viewport.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'&&!e.target.closest('a,button'))touch={x:e.clientX,y:e.clientY,id:e.pointerId}});
viewport.addEventListener('pointerup',e=>{if(!touch||touch.id!==e.pointerId)return;const dx=e.clientX-touch.x,dy=e.clientY-touch.y;touch=null;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5&&multiple)showSlide(current+(dx<0?1:-1),true)});
viewport.addEventListener('pointercancel',()=>{touch=null});
motion.addEventListener('change',()=>{if(motion.matches){paused=true;img.getAnimations().forEach(a=>a.cancel());schedule()}});
document.addEventListener('visibilitychange',schedule);
img.addEventListener('load',()=>{img.style.visibility='visible'});img.addEventListener('error',()=>{img.style.visibility='hidden'});if(img.complete&&!img.naturalWidth)img.style.visibility='hidden';
schedule();
}
const search=document.getElementById('service-search');
if(search){const filterButtons=[...document.querySelectorAll('[data-filter]')],cards=[...document.querySelectorAll('.card')],params=new URLSearchParams(location.search);let category=params.get('category')||'all';if(!filterButtons.some(b=>b.dataset.filter===category))category='all';search.value=(params.get('q')||'').slice(0,100);
function filterServices(updateUrl=true){const terms=search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);let visible=0;cards.forEach(card=>{const match=(category==='all'||card.dataset.category===category)&&terms.every(term=>card.dataset.search.includes(term));card.hidden=!match;if(match)visible++});filterButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===category)));document.getElementById('category-value').value=category;document.getElementById('results-count').textContent=visible+' '+(visible===1?'solution':'solutions')+' found';document.getElementById('empty-results').hidden=visible!==0;if(updateUrl){const url=new URL(location.href);if(search.value.trim())url.searchParams.set('q',search.value.trim());else url.searchParams.delete('q');if(category!=='all')url.searchParams.set('category',category);else url.searchParams.delete('category');history.replaceState(null,'',url.pathname+url.search+url.hash)}}
search.addEventListener('input',()=>filterServices());search.form.addEventListener('submit',e=>{e.preventDefault();filterServices()});filterButtons.forEach(b=>b.addEventListener('click',()=>{category=b.dataset.filter;filterServices()}));document.getElementById('reset-search').addEventListener('click',()=>{search.value='';category='all';filterServices();search.focus()});filterServices(false);
}
if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches&&'IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('reveal');observer.unobserve(entry.target)}}),{threshold:.08});document.querySelectorAll('.card,.step').forEach(el=>observer.observe(el))}

document.querySelectorAll('[data-service]').forEach(link=>link.addEventListener('click',()=>{document.getElementById('sport').value=link.dataset.service}));
document.getElementById('enquiry').addEventListener('submit',event=>{event.preventDefault();const f=new FormData(event.target),message=`Hello Likitha Sports!\nName: ${f.get('name')}\nPhone: ${f.get('phone')}\nLocation: ${f.get('location')}\nInterested in: ${f.get('sport')}\nProject details: ${f.get('message')}`;window.location.href='https://wa.me/918179655506?text='+encodeURIComponent(message)});
document.getElementById('year').textContent=new Date().getFullYear();
</script></body></html>'''
def service_icon(category, number):
    paths = {
        'court': '<rect x="8" y="12" width="56" height="48" rx="2"/><path d="M36 12v48M8 36h56"/><circle cx="36" cy="36" r="10"/>',
        'field': '<rect x="8" y="10" width="56" height="52" rx="25"/><rect x="15" y="17" width="42" height="38" rx="18"/><path d="M36 17v38"/>',
        'facility': '<path d="M7 31 36 13l29 18M13 29v33h46V29M25 62V39h22v23M7 62h58"/>',
    }
    return '<div class="card-symbol"><svg viewBox="0 0 72 72" aria-hidden="true">' + paths[category] + '</svg><b aria-hidden="true">' + str(number).zfill(2) + '</b></div>'


def render_card(service, number, visible=True):
    s = service
    title = escape(s['title'])
    search_text = escape(' '.join([s['title'], s['summary'], CATEGORIES[s['category']], *s['scope']]).casefold(), quote=True)
    if s['image']:
        visual = '<div class="card-image"><img src="' + escape(cms.image_url(s['image']), quote=True) + '" alt="' + title + '" width="600" height="400" loading="lazy"></div>'
    else:
        visual = service_icon(s['category'], number)
    hidden = '' if visible else ' hidden'
    return f'<article class="card" data-category="{s["category"]}" data-slug="{s["slug"]}" data-search="{search_text}"{hidden}>{visual}<div class="card-body"><span class="label">{escape(CATEGORIES[s["category"]]).upper()} / {number:02}</span><h3>{title}</h3><p>{escape(s["summary"])}</p><a href="/services/{s["slug"]}">Explore solution <span aria-hidden="true">↗</span></a></div></article>'


def home_page(query_string='', content=None):
    content = content or cms.load_content()
    services = cms.published_services(content)
    params = parse_qs(query_string)
    query = params.get('q', [''])[0][:100]
    category = params.get('category', ['all'])[0]
    if category not in (*CATEGORIES, 'all'):
        category = 'all'
    matches = {s['slug'] for s in find_services(query, category, services)}
    cards = ''.join(render_card(s, i, s['slug'] in matches) for i, s in enumerate(services, 1))
    page = PAGE.replace('__SERVICE_CARDS__', cards)
    # Feature published solutions; favour the owner's uploaded imagery.
    featured = sorted(services, key=lambda item: not str(item.get('image') or '').startswith('/media/'))[:3]
    project_cards = []
    for i, item in enumerate(featured, 1):
        title = escape(item['title'])
        image = cms.image_url(item.get('image'))
        visual = ('<div class="project-photo"><img src="' + escape(image, quote=True) + '" alt="' + title + '" width="600" height="400" loading="lazy"></div>') if image else service_icon(item['category'], i)
        project_cards.append('<article class="project-card">' + visual + '<div class="project-copy"><p>' + escape(CATEGORIES[item['category']]) + '</p><h3>' + title + '</h3><a href="/services/' + escape(item['slug'], quote=True) + '">Explore project options <span aria-hidden="true">↗</span></a></div></article>')
    page = page.replace('__PROJECT_CARDS__', ''.join(project_cards))
    page = page.replace('placeholder="Search courts, pools, tracks…" value=""', 'placeholder="Search courts, pools, tracks…" value="' + escape(query, quote=True) + '"')
    page = page.replace('name="category" value="all"', 'name="category" value="' + category + '"')
    for key in ('all', *CATEGORIES):
        page = page.replace(f'data-filter="{key}" aria-pressed="' + ('true' if key == 'all' else 'false') + '"', f'data-filter="{key}" aria-pressed="' + str(key == category).lower() + '"')
    count = len(matches)
    page = page.replace('9 solutions available', f'{count} ' + ('solution' if count == 1 else 'solutions') + ' found')
    if not matches:
        page = page.replace('id="empty-results" hidden', 'id="empty-results"')
    hero = content['hero']
    page = page.replace('Great spaces.<br><span>Greater games.</span>', escape(hero['line1']) + '<br><span>' + escape(hero['line2']) + '</span>')
    page = page.replace('Courts, turfs and sports infrastructure.<br>From your first idea to the first game.', escape(hero['description']))
    slides = [dict(slide, image=cms.image_url(slide['image'])) for slide in content['slides']]
    slides_json = json.dumps(slides, ensure_ascii=False).replace('<', '\\u003c')
    page = re.sub(r'const slides=\[.*?\];', lambda _: 'const slides=' + slides_json + ';', page, count=1)
    first = content['slides'][0]
    page = re.sub(r'src="https://likithasports.com/assets/home/football-truf.webp" width="650" height="650" alt="Football turf"', lambda _: 'src="' + escape(cms.image_url(first['image']), quote=True) + '" width="650" height="650" alt="' + escape(first['alt'], quote=True) + '"', page, count=1)
    page = page.replace('id="slide-category">FIELDS & TURFS / 01', 'id="slide-category">' + escape(first['category']))
    page = page.replace('id="slide-title">More room for your game.', 'id="slide-title">' + escape(first['title']))
    dots = ''.join('<button class="dot" type="button" aria-controls="hero-viewport" aria-label="Show slide ' + str(i) + ': ' + escape(slide['alt'], quote=True) + '" aria-pressed="' + str(i == 1).lower() + '"></button>' for i, slide in enumerate(content['slides'], 1))
    page = page.replace('__SLIDE_DOTS__', dots)
    page = page.replace('id="slide-number" aria-hidden="true">01 / 03', 'id="slide-number" aria-hidden="true">01 / ' + str(len(slides)).zfill(2))
    options = ''.join('<option>' + escape(item['title']) + '</option>' for item in services) + '<option>Other sports infrastructure</option>'
    page = re.sub(r'(<select id="sport" name="sport">).*?(</select>)', lambda m: m[1] + options + m[2], page, count=1, flags=re.S)
    return page


def service_page(slug, content=None):
    content = content or cms.load_content()
    services = cms.published_services(content)
    service = next((s for s in services if s['slug'] == slug), None)
    if service is None:
        return None
    s = service
    title = escape(s['title'])
    if s['image']:
        visual = f'<img class="detail-image" src="{escape(cms.image_url(s['image']), quote=True)}" alt="{title}" width="650" height="420" fetchpriority="high">'
    else:
        visual = '<div class="detail-art">' + service_icon(s['category'], services.index(s) + 1) + f'<h2>{title}</h2><p>Planned around your space. Built around your game.</p></div>'
    scope = ''.join('<li>' + escape(item) + '</li>' for item in s['scope'])
    related = [other for other in services if other['slug'] != slug]
    related.sort(key=lambda other: other['category'] != s['category'])
    links = ''.join(f'<a href="/services/{other["slug"]}">{escape(other["title"])} ↗</a>' for other in related[:3])
    details = f'''<section class="detail-hero"><div class="wrap"><div class="breadcrumb"><a href="/">Home</a> / <a href="/#solutions">Solutions</a> / {title}</div><div class="detail-grid"><div><p class="eyebrow">{escape(CATEGORIES[s['category']])}</p><h1>{title}</h1><p>{escape(s['summary'])}</p><div class="actions tw:flex tw:flex-wrap tw:gap-3"><a class="btn green" href="#contact">Enquire about this solution ↗</a><a class="btn outline" href="/#solutions">All solutions</a></div></div>{visual}</div></div></section><section class="section"><div class="wrap detail-content"><div><p class="eyebrow">Your project, considered</p><h2>Let's talk about the details.</h2><ul class="scope-list">{scope}</ul><p style="font-size:12px;color:var(--muted)">The final scope is agreed around your site and requirements.</p></div><aside class="planning-box"><h3>A good place to start</h3><p>{escape(s['prompt'])}</p><p>Have a drawing or site plan? Mention it in your enquiry and discuss it with our team on WhatsApp.</p><a class="btn" href="#contact">Share your project ↗</a></aside></div></section><section class="section about"><div class="wrap"><p class="eyebrow">Keep exploring</p><h2>More possibilities for your space.</h2><div class="related-links">{links}</div></div></section>'''
    page = re.sub(r'<section class="hero".*?(?=<section class="section" id="faq">)', lambda _: details, home_page('', content), count=1, flags=re.S)
    page = page.replace('<title>Likitha Sports | Sports Surfaces & Infrastructure</title>', f'<title>{title} | Likitha Sports</title>')
    page = page.replace('content="Sports surfaces, courts, turfs and infrastructure for schools, academies and communities. Build your next sports space with Likitha Sports."', 'content="' + escape(s['summary'], quote=True) + ' Discuss your project with Likitha Sports."')
    page = page.replace('<option>' + title + '</option>', '<option selected>' + title + '</option>')
    return page



def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    if path.startswith('/api/admin/') or path.startswith('/media/'):
        return cms.handle(environ, start_response)
    if path in ('/dashboard', '/dashboard/', '/dashboard/setup'):
        if method not in ('GET', 'HEAD'):
            return cms.response(start_response, 405, {'error': 'Use GET or HEAD.'}, [('Allow', 'GET, HEAD')])
        body = dashboard.PAGE.encode('utf-8')
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(body))), ('Cache-Control', 'no-store'), ('X-Robots-Tag', 'noindex, nofollow'), ('X-Frame-Options', 'DENY'), ('X-Content-Type-Options', 'nosniff'), ('Referrer-Policy', 'no-referrer'), ('Content-Security-Policy', "default-src 'self'; img-src 'self' https://likithasports.com data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")])
        return [b'' if method == 'HEAD' else body]
    if method not in ('GET', 'HEAD'):
        status, content_type, body = '405 Method Not Allowed', 'text/plain; charset=utf-8', b'Method not allowed'
    elif path == '/':
        status, content_type, body = '200 OK', 'text/html; charset=utf-8', home_page(environ.get('QUERY_STRING', '')).encode('utf-8')
    elif path.startswith('/services/'):
        slug = path[len('/services/'):].rstrip('/')
        page = service_page(slug)
        status, content_type, body = ('200 OK', 'text/html; charset=utf-8', page.encode('utf-8')) if page else ('404 Not Found', 'text/plain; charset=utf-8', b'Service not found')
    elif path == '/api/services':
        query = parse_qs(environ.get('QUERY_STRING', ''))
        term = query.get('q', [''])[0][:100]
        category = query.get('category', ['all'])[0]
        if category not in (*CATEGORIES, 'all'):
            status, content_type, body = '400 Bad Request', 'application/json', b'{"error":"Unknown category"}'
        else:
            items = find_services(term, category, cms.published_services(cms.load_content()))
            status, content_type, body = '200 OK', 'application/json; charset=utf-8', json.dumps({'services': items, 'count': len(items)}, ensure_ascii=False).encode('utf-8')
    elif path == '/assets/tailwind.css':
        status, content_type, body = '200 OK', 'text/css; charset=utf-8', (LOGO_PATH.parent / 'tailwind.css').read_bytes()
    elif path == '/logo.png':
        status, content_type, body = '200 OK', 'image/png', LOGO_PATH.read_bytes()
    elif path == '/healthz':
        status, content_type, body = '200 OK', 'application/json', b'{"status":"ok"}'
    elif path == '/robots.txt':
        status, content_type, body = '200 OK', 'text/plain', b'User-agent: *\nAllow: /\n'
    elif path == '/favicon.ico':
        status, content_type, body = '204 No Content', 'image/x-icon', b''
    else:
        status, content_type, body = '404 Not Found', 'text/plain; charset=utf-8', b'Page not found'
    headers = [('Content-Type', content_type), ('Content-Length', str(len(body))), ('X-Content-Type-Options', 'nosniff'), ('Referrer-Policy', 'strict-origin-when-cross-origin'), ('X-Frame-Options', 'SAMEORIGIN')]
    if path in ('/logo.png', '/assets/tailwind.css') and status == '200 OK':
        headers.append(('Cache-Control', 'public, max-age=86400'))
    if status.startswith('405'):
        headers.append(('Allow', 'GET, HEAD'))
    start_response(status, headers)
    return [b'' if method == 'HEAD' else body]

if __name__ == '__main__':
    with make_server('0.0.0.0', int(os.environ.get('PORT', '8000')), app) as server:
        server.serve_forever()
