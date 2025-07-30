바우카를 이용하여 파이썬을 배우기 위한 모듈입니다.
this module for study python with bowcar hardware.

arduino-cli 프로그램의 설치가 필수입니다.
this module need 'arduino-cli' program.

명령어

0. 시간 지연 관련
    BowCar.delay(time) : time(ms)만큼 지연
1. led 관련
    BowCar.red_on() : 빨간 led 켜기
    BowCar.red_off() : 파란 led 끄기
    BowCar.blue_on() : 파란 led 켜기
    BowCar.blue_off() : 파란 led 끄기
    BowCar.all_light_on() : 모든 led 켜기
    BowCar.all_light_off() : 모든 led 끄기
2. 부저 관련
    BowCar.buzzer_on(scale, octave, note) : octave의 scale에 해당하는 음을 note음표 만큼 실행
    BowCar.buzzer_off() : 부저 끄기
    BowCar.set_duration(time) : 부저음의 기본 길이를 time(ms)만큼 조정