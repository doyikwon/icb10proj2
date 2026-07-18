"""
NutriMatch (NutriFit) 대시보드 메인 앱 (app.py)
작성자: Antigravity
작성일: 2026-07-18
역할: Tailwind CSS를 Native DOM에 주입하며, 마크다운 렌더링 충돌 방지 처리가 적용된 메인 랜딩페이지입니다.
"""

import streamlit as st
import re

# 페이지 기본 설정
st.set_page_config(
    page_title="NutriMatch | 개인 맞춤형 영양 진단",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
if 'agreed' not in st.session_state:
    st.session_state.agreed = False
    
if 'answers' not in st.session_state:
    st.session_state.answers = {
        'gender': None,
        'age': None,
        'height': 0,
        'weight': 0,
        'exercise': None,
        'alcohol': None,
        'smoking': None,
        'allergies': [],
        'diseases': [],
        'current_supplements': [],
        'goals': [],
        'pill_discomfort': None,
        'budget': None
    }

# CSS 주입 부분
css_content = """
    <!-- Tailwind CSS 2.2.19 CDN -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <!-- Google Fonts & FontAwesome -->
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    header { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    body { font-family: 'Noto Sans KR', sans-serif !important; background-color: #FAF9F6 !important; }
    .font-serif { font-family: 'Lora', serif !important; }
    
    .text-\\[\\#1E3A2F\\] { color: #1E3A2F !important; }
    .bg-\\[\\#1E3A2F\\] { background-color: #1E3A2F !important; }
    .hover\\:bg-\\[\\#142820\\]:hover { background-color: #142820 !important; }
    .text-\\[\\#10B981\\] { color: #10B981 !important; }
    .bg-\\[\\#10B981\\] { background-color: #10B981 !important; }
    .hover\\:text-\\[\\#10B981\\]:hover { color: #10B981 !important; }
    .border-\\[\\#10B981\\] { border-color: #10B981 !important; }
    .from-\\[\\#FAF9F6\\] { --tw-gradient-from: #FAF9F6 !important; --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(250, 249, 246, 0)) !important; }
    
    .pulse-red { animation: pulse-red-animation 1.5s infinite; }
    @keyframes pulse-red-animation {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    </style>
"""
st.markdown(re.sub(r'\n\s*', ' ', css_content), unsafe_allow_html=True)

# 메인 콘텐츠 (들여쓰기로 인한 마크다운 코드블록 변환 방지 처리)
html_content = """
<div class="flex flex-col min-h-screen text-slate-700 antialiased" style="background-color: #FAF9F6; width: 100vw; min-height: 100vh;">
<header class="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-100 shadow-sm" style="background-color: rgba(255,255,255,0.9);">
    <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <a href="#" class="flex items-center gap-2" style="text-decoration: none;">
            <div class="w-10 h-10 rounded-xl bg-[#1E3A2F] flex items-center justify-center text-white" style="background-color: #1E3A2F;">
                <i class="fa-solid fa-seedling text-lg text-[#10B981]" style="color: #10B981;"></i>
            </div>
            <span class="font-serif text-2xl font-bold text-[#1E3A2F] tracking-tight" style="color: #1E3A2F;">Nutri<span class="text-[#10B981]" style="color: #10B981;">Match</span></span>
        </a>
        <nav class="hidden md:flex items-center gap-8">
            <a href="#" class="font-medium text-gray-600 hover:text-[#1E3A2F] transition" style="text-decoration: none;">소개</a>
            <a href="Intro" target="_self" class="font-medium text-gray-600 hover:text-[#1E3A2F] transition" style="text-decoration: none;">AI 맞춤 추천</a>
            <a href="Dashboard" target="_self" class="font-medium text-[#10B981] flex items-center gap-1.5 transition font-bold" style="color: #10B981; text-decoration: none;">
                <i class="fa-solid fa-triangle-exclamation"></i> 내 영양제 초과 진단
            </a>
            <a href="#" class="font-medium text-gray-600 transition" style="text-decoration: none;">커뮤니티</a>
        </nav>
    </div>
</header>
<main class="flex-grow">
    <div class="py-16 sm:py-24 bg-gradient-to-b from-[#FAF9F6] to-white" style="background: linear-gradient(to bottom, #FAF9F6, white);">
        <div class="max-w-7xl mx-auto px-6 space-y-24">
            
            <div class="grid md:grid-cols-12 gap-12 items-center">
                <div class="md:col-span-7 space-y-6">
                    <span class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border text-xs font-bold tracking-wide" style="background-color: #ecfdf5; border-color: #d1fae5; color: #10B981;">
                        <i class="fa-solid fa-shield-heart"></i> AI 기반 1:1 개인 맞춤형 영양 케어
                    </span>
                    <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black font-serif leading-tight tracking-tight" style="color: #1E3A2F; line-height: 1.2;">
                        더 이상 넘겨짚지 마세요.<br>내 몸에 꼭 맞는<br><span style="color: #10B981;">안심 영양 설계</span>
                    </h1>
                    <p class="text-gray-500 text-sm sm:text-base leading-relaxed max-w-lg" style="color: #64748b; font-size: 1.125rem;">
                        복잡한 23개의 신체 변수와 지병 상태를 완벽 분석하여 부작용 위험 0% 수준의 영양제 추천 및 초과 중복 섭취 필터 대시보드를 제공합니다.
                    </p>
                    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-3">
                        <a href="Intro" target="_self" class="text-white font-bold px-8 py-4 rounded-2xl shadow-xl transition duration-300 text-center text-base inline-block cursor-pointer" style="background-color: #1E3A2F; text-decoration: none;">
                            무료 건강 설문 시작하기 <i class="fa-solid fa-arrow-right ml-1.5 text-xs"></i>
                        </a>
                        <a href="Dashboard" target="_self" class="bg-white border-2 font-bold px-8 py-4 rounded-2xl transition duration-300 text-center text-base inline-block cursor-pointer" style="border-color: #e2e8f0; color: #334155; text-decoration: none;">
                            내 영양제 자가진단 검사
                        </a>
                    </div>
                </div>
                
                <div class="md:col-span-5 relative">
                    <div class="absolute -inset-4 rounded-full blur-3xl z-0" style="background-color: rgba(16, 185, 129, 0.15);"></div>
                    <div class="relative z-10 bg-white p-8 rounded-3xl border border-gray-100 shadow-2xl space-y-6">
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-white px-2.5 py-1 rounded font-bold uppercase tracking-wider" style="background-color: #1E3A2F;">AI Medical Filter Verified</span>
                            <i class="fa-solid fa-heart-pulse text-red-500 text-lg pulse-red"></i>
                        </div>
                        <div class="space-y-4">
                            <div class="p-3.5 rounded-2xl border flex gap-3.5" style="background-color: rgba(236, 253, 245, 0.5); border-color: rgba(209, 250, 229, 0.5);">
                                <i class="fa-solid fa-shield-virus text-xl mt-1" style="color: #10B981;"></i>
                                <div>
                                    <span class="text-xs font-bold block" style="color: #1E3A2F;">흡연자 특별 필터 탑재</span>
                                    <p class="text-[11px] text-gray-500 mt-1" style="font-size: 0.8rem;">흡연자의 폐암 유발 확률을 높이는 고농도 베타카로틴 성분을 자동 우회·원천 차단합니다.</p>
                                </div>
                            </div>
                            <div class="p-3.5 rounded-2xl border flex gap-3.5" style="background-color: rgba(254, 252, 232, 0.5); border-color: rgba(254, 240, 138, 0.5);">
                                <i class="fa-solid fa-capsules text-xl mt-1" style="color: #d97706;"></i>
                                <div>
                                    <span class="text-xs font-bold block" style="color: #92400e;">복용 약물 시너지 가미</span>
                                    <p class="text-[11px] text-gray-500 mt-1" style="font-size: 0.8rem;">고혈압, 당뇨 및 항응고제 섭취자를 위해 혈액 응고 방지 중복 충돌을 조율합니다.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="grid sm:grid-cols-3 gap-8 pt-12 border-t border-gray-100 mt-12">
                <div class="space-y-3">
                    <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background-color: #ecfdf5; color: #10B981;">
                        <i class="fa-solid fa-chart-bar text-xl"></i>
                    </div>
                    <h3 class="font-bold text-lg" style="color: #1E3A2F;">23개 정밀 신체 변수 연산</h3>
                    <p class="text-xs text-gray-400 leading-normal" style="font-size: 0.9rem;">성별, BMI, 수면 패턴, 알레르기 및 만성질환을 조합한 다차원 추천 설계를 제공합니다.</p>
                </div>
                <div class="space-y-3">
                    <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background-color: #ecfdf5; color: #10B981;">
                        <i class="fa-solid fa-triangle-exclamation text-xl"></i>
                    </div>
                    <h3 class="font-bold text-lg" style="color: #1E3A2F;">중복·오버도즈 자가진단</h3>
                    <p class="text-xs text-gray-400 leading-normal" style="font-size: 0.9rem;">현재 먹는 영양소들이 내 몸 상태에 적합한지 안전 한계선(Tolerable Upper Intake)으로 조율합니다.</p>
                </div>
                <div class="space-y-3">
                    <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background-color: #ecfdf5; color: #10B981;">
                        <i class="fa-solid fa-cart-shopping text-xl"></i>
                    </div>
                    <h3 class="font-bold text-lg" style="color: #1E3A2F;">정밀 아웃링크 가격비교</h3>
                    <p class="text-xs text-gray-400 leading-normal" style="font-size: 0.9rem;">쿠팡, 아이허브, 올리브영에 판매 중인 최적의 건강기능식품 구매처로 직접 원스톱 가이드합니다.</p>
                </div>
            </div>
        </div>
    </div>
</main>
</div>
"""

# 마크다운 렌더링 에러 방지를 위해 줄바꿈과 연속된 공백 제거
html_content = re.sub(r'\n\s*', ' ', html_content)
st.markdown(html_content, unsafe_allow_html=True)
