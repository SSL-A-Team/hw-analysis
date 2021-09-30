clear
clc

% if this fails run pkg install -forge optim
pkg load optim

%% Notes
% 90deg on the plot is "forward"
% wheelConfig should be entered in degrees
%   Angles measured from the axis running left-to-right




%% User Configurable Parameters

% robot mechanical params
robotMass_kg = 2.5;
gearRatio = "1:1.4";
wheelDiameter_mm = 70;
obsMaxAcceleration_m_s2 = 2.5;
obsMaxVelocity_m_s = 4.5;
obsMaxAccelFF = 0.80;
wheelConfig = [ % Front/Rear Wheel Angles
  [45 45];
  [30 60];
  [30 37];
  %[30 45];
  [35 45];
]

% robot electrical params


% field params
fieldWidth_m = 13.4;
fieldHeight_m = 10.4;
fieldDim_m = [fieldWidth_m fieldHeight_m]; 
fieldDiag = norm(fieldDim_m);

df45_ratedVoltage = 24; % volts
df45_l2lResistance = 0.800; % ohms
df45_50_torqueSamples = [0.011 0.027 0.048 0.060 0.081 0.111 0.271 0.376 0.459 0.481];
df45_50_speedSamples =  [6065  5781  5518  5385  5174  4840  3017  2011  1017  544  ];
df45_50_minSpeedAtRatedPower_rpm = 5260;
df45_50_torqueConstant_Nm_A = 0.0335;

df45_stallCurrent = df45_ratedVoltage ./ df45_l2lResistance;
% these values seem reasonable, but high
df45_stallTorque = df45_stallCurrent .* df45_50_torqueConstant_Nm_A;
df45_stallWattage = df45_stallCurrent .* df45_ratedVoltage;

length(df45_50_torqueSamples);
size(df45_50_torqueSamples);
F = [ones(length(df45_50_torqueSamples), 1), df45_50_torqueSamples(:)];
%[p, e_var, r, p_var, fit_var] = LinearRegression(F, df45_50_speedSamples(:))
[p, ~, ~, ~, ~] = LinearRegression(F, df45_50_speedSamples(:));
b = p(1)
m = p(2)

torques = linspace(0, 0.50, 100);
speeds = torques .* m + b;

% plot(torques, speeds)

% force = mass * acceleration

maxAcceleration_m_s2 = obsMaxAcceleration_m_s2 * obsMaxAccelFF;
maxAppliedForce = robotMass_kg * maxAcceleration_m_s2;
% assume our wheels have worse traction by a fudgeFactor (controls limited to prevent slippage)

% dist = 1/2 * a * t^2
% sqrt((2 * dist)) / a = t

travelTime = sqrt((2 .* fieldDiag) / maxAppliedForce)

return

sampleCount = 1e5;





%% Calculation Steps

function output = fourWheelRefConvert(frontAngle,rearAngle)
  # convert the front/rear wheel angle from horizontal to [0,360) with 0deg=fwd
  output = [90-frontAngle 90+rearAngle 270-rearAngle 270+frontAngle];
end

wheelAngleDeg = {};
legendLabel = [];
stats = [];

for i=1:size(wheelConfig,1)
  wheelAngleDeg = [
    wheelAngleDeg;
    {fourWheelRefConvert(wheelConfig(i,1),wheelConfig(i,2))}
  ];
  legendLabel = [legendLabel;{[num2str(wheelConfig(i,1)) '-' num2str(wheelConfig(i,2))]}];
end
wheelAngleDeg

# Convert wheel angles to radians
wheelAngleRad = cellfun(@(deg) deg2rad(deg),wheelAngleDeg,'un',0);

plotStyle = {'-r' '-g' '-b' '--r' '--g' '--b'};

# Robot-level Vectors
theta = deg2rad(linspace(0,360,sampleCount)); # robot heading
robotVelocity = [cos(theta);sin(theta);zeros(1,sampleCount)];

# Iterate over each wheel config
for i=1:length(wheelAngleDeg)
  phi = wheelAngleRad{i}; # load wheel config

  psi = [
    theta - phi(1);
    theta - phi(2);
    theta - phi(3);
    theta - phi(4);
  ];
  psi = psi - (pi/2); %force applied by the wheel is orthonormal to the shaft

  # Fwd/Inv kinematic model
  fkArr = [
    -sin(phi);
     cos(phi);
     ones(1, length(wheelAngleDeg{i}))]; % constant omega
  ikArr = pinv(fkArr);

  # Calculate individual wheel velocities based on robot velocity vector
  wheelVelocities = ikArr*robotVelocity;
  
  scaledWheelVelocities = wheelVelocities ./ max(abs(wheelVelocities),[],1);
  maxRobotVelocity = fkArr*scaledWheelVelocities;
  maxRobotVelocity_angle = atan2(maxRobotVelocity(2,:),maxRobotVelocity(1,:));
  maxRobotVelocity_magnitude = sqrt(maxRobotVelocity(1,:).^2+maxRobotVelocity(2,:).^2);

  test = size(scaledWheelVelocities)
  
  usefulWheelPower = [
    scaledWheelVelocities(1)*cos(psi(1,:));
    scaledWheelVelocities(2)*cos(psi(2,:));
    scaledWheelVelocities(3)*cos(psi(3,:));
    scaledWheelVelocities(4)*cos(psi(4,:));
  ];
  fightingWheelPower = [
    scaledWheelVelocities(1,:).*sin(psi(1,:));
    scaledWheelVelocities(2,:).*sin(psi(2,:));
    scaledWheelVelocities(3,:).*sin(psi(3,:));
    scaledWheelVelocities(4,:).*sin(psi(4,:));
  ];
  fightingWheelPower = abs(fightingWheelPower);
  usefulWheelPower = abs(usefulWheelPower);
  
  meanFightingWheelPower = mean(fightingWheelPower,1);
  sumFightingWheelPower = sum(fightingWheelPower,1);
  maxFightingWheelPower = max(fightingWheelPower);

  
  scaledWheelVelocities = abs(scaledWheelVelocities);
  maxScaledwheelVelocity = max(scaledWheelVelocities);
  stdScaledwheelVelocity = std(scaledWheelVelocities);
  covScaledwheelVelocity = std(scaledWheelVelocities)/mean(scaledWheelVelocities);
  rangeScaledwheelVelocity = max(scaledWheelVelocities) - min(scaledWheelVelocities);
  
  stats = [
    stats;
    min(maxRobotVelocity_magnitude) max(maxRobotVelocity_magnitude) mean(maxRobotVelocity_magnitude) std(maxRobotVelocity_magnitude) std(maxRobotVelocity_magnitude)/mean(maxRobotVelocity_magnitude)
  ];
  
  subplot(1,2,1);
  if(i == 1)
    hold off
  else
    hold on
  end
  # Plot with the Forward direction = 90deg
  title("Maximum Applicable Unit Force (in motors)")
  polar(maxRobotVelocity_angle+pi/2,maxRobotVelocity_magnitude,plotStyle{i});
  
  subplot(1,2,2);
  if(i == 1)
    hold off
  else
    hold on
  end
  title("Fighting Force (direct internal loss)")
  polar(theta+pi/2,maxFightingWheelPower,plotStyle{i});
  %polar(theta+pi/2,meanFightingWheelPower,plotStyle{i+3});
  %polar(theta+pi/2,rangeScaledwheelVelocity,plotStyle{i});

end

##subplot(1,2,1)
##hold off
##polar(theta+pi/2,fightingWheelPower(1,:),'--b');
##hold on
##polar(theta+pi/2,fightingWheelPower(2,:),'-b');
##polar(theta+pi/2,fightingWheelPower(3,:),'-r');
##polar(theta+pi/2,fightingWheelPower(4,:),'--r');
##
##subplot(1,2,2)
##hold off
##polar(theta+pi/2,scaledWheelVelocities(1,:),'--b');
##hold on
##polar(theta+pi/2,scaledWheelVelocities(2,:),'-b');
##polar(theta+pi/2,scaledWheelVelocities(3,:),'-r');
##polar(theta+pi/2,scaledWheelVelocities(4,:),'--r');


subplot(1,2,1);
legend(legendLabel);

subplot(1,2,2);
%legend([legendLabel;legendLabel]);
legend(legendLabel);



display('Label        Min         Max         Mean       StdDev      CoV');
legendLabel
display(horzcat(legendLabel.', num2str(stats)));
