### SKKU 2020 spring 41 class
# team3

##### Product price and news information system

***
## Team member

    2016310978 강승룡
    2017313172 고성현
    2017313114 김지우
    2017314749 유민종
    2014312692 이병건
    2014313003 최현우

***
## github structure

    team3┐
         ┣ docs ┐
                ┣ proposal.pptx
                ┣ proposal.pdf
                ┣ Design_specification_spring2020_team3.pdf
                └ requirement_specification_spring2020_team3.pdf
         └ src  - newShop   ┐
                            ┣ Auth (로그인 관련)
                            ┣ Display (홈페이지 관련)
                            ┣ NewShop
                            └ manage.py
***
## module dependency (how to run)

    pip install django
    pip install django-extensions
    pip install pandas
    pip install requests
    pip install bs4
    pip install numpy
    pip insatll torch torchvision # For Linux
    pip install torchtext
    python3 -m pip install konlpy # For Linux
    python -m pip install -U matplotlib
    pip install WordCloud
    
    python manage.py runserver
  For Pytorch see [here](https://pytorch.org/get-started/locally/). For KoNLPy see [here](https://konlpy-ko.readthedocs.io/ko/latest/install/).
***
#### 테스트 사이트 : http://sr97.pythonanywhere.com/
##### 테스트 사이트는 즉시 반영이 아니라 수동 반영이므로, 여기에 푸시를 한 이후에는 조장에게 말하고 기다려 주세요.
##### 테스트 사이트는 개발 중 테스트에만 사용되며, 시연에는 사용되지 않습니다. 시연은 로컬로 진행됩니다.



