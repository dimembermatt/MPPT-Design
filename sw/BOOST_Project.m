%%BOOST CONVERTER SCRIPT
%PARAMETERS REQUIRED
Vi = 16;
Vo = 48;
Po = 250; %250W full load
RRL = 0.2; %Ripple Ratio Ind
RRCo = 0.04; %Ripple Ratio Cap Out
RRCi = 0.0125; %Ripple Ratio Cap In

%conduction loss parasitic parameters:
ResrL = 0.01;

Coss = 550*10^-12;
Ron = 7.5*10^-3;
f = 50000; %frequency

%%Duty, Load, Current(I/O)
D = (Vo - Vi)/Vo;
RLoad = (Vo^2)/(Po);
Ii = Po/Vi;
Io = Po/Vo;

%%inductance, ripple ratio
L = ((Vi^2)/(2*Po*f*RRL))*(1-(Vi/Vo));

%%capacitance ripple ratio
Co = (Po/(2*RRCo*f*(Vo^2)))*(1-(Vi/Vo));

%%input capacitance ripple ratio
Ci = (RRL*Po)/(8*f*RRCi*(Vi^2));

%*************************RMS + LOSSES*******************************
%%switch1 parameters
IrmsSW1 = sqrt(D*( ((Po/Vi)^2) + (1/3)*(Po*RRL/Vi)^2 ));
IavgSW1 = (Po/Vi)*(1-Vi/Vo);
PlossSW1 = Ron*(IrmsSW1^2);

%%switch2 parameters
IrmsSW2 = sqrt((1-D)*( ((Po/Vi)^2) + (1/3)*(Po*RRL/Vi)^2 ));
IavgSW2 = (Po/Vo);
PlossSW2 = Ron*(IrmsSW2^2);

%%Inductor parameters
IrmsL = sqrt( ((Po/Vi)^2) + (1/3)*(Po*RRL/Vi)^2 );
IavgL = Po/Vi;
PlossL = ResrL*(IrmsL^2);

%Switching Loss:
Pswitching = (Coss + Coss)*(Vo^2)*f;
Pconduction = PlossSW1 + PlossSW2;

%deadtime minimum
td = (2*Vi*Vo*Coss)/(Po*(1+RRL));

%%
%*************************ASSUMING MOSFET SW2******************************

Vi = 16;
RRL = 0.2;
Coss = 550*10^-12;
tau = 4.12*10^-12;
Ron = linspace(0,0.01,100);
f = 450000; %frequency

%%Switch parameters 
Ploss_cond = Ron*( ((Po/Vi)^2) + (1/3)*(Po*RRL/Vi)^2 );
Ploss_switch = (tau./Ron)*Vo^2*f;
Ploss_csw = Ploss_cond + Ploss_switch;

figure 
plot(Ron, Ploss_cond);
title('Conduction Loss vs Ron');

hold on
plot(Ron, Ploss_switch);
title('Switching Loss vs Ron');

hold on
plot(Ron, Ploss_csw);
title('Total Loss vs Ron');

legend({'Pcond','Psw','Ptotal'});


%%
%%FOR ACTUAL CALCULATIONS
Vi = 16;
RRL = 0.2;
Coss = 1.64*10^-9;
tau = 12.63*10^-12;
Ron = 7.7*10^-3;
f = linspace(100000, 900000, 1000); %frequency

%%Switch parameters 
Ploss_cond = Ron*( ((Po/Vi)^2) + (1/3)*(Po*RRL/Vi)^2 );
Ploss_switch = (tau/Ron)*Vo^2.*f;
Ploss_csw = Ploss_cond + Ploss_switch;

figure 
%plot(f, Ploss_cond);
title('Conduction Loss vs f');

hold on
plot(f, Ploss_switch);
title('Switching Loss vs f');

hold on
plot(f, Ploss_csw);
title('Total Loss vs f');
hold on

legend({'Psw','Ptotal'});