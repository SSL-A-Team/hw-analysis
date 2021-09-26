clear
clc

%% Notes
% 90deg on the plot is "forward"
% wheelConfig should be entered in degrees
%   Angles measured from the axis running left-to-right




%% User Configurable Parameters

wheelConfig = [ % Front/Rear Wheel Angles
  [45 45];
  [30 60];
  [30 45];
  %[35 45];
]

sampleCount = 1e5;




%% Calculation Steps

function output = fourWheelRefConvert(frontAngle,rearAngle)
  # convert the front/rear wheel angle from horizontal to [0,360) with 0deg=fwd
  output = [90-frontAngle 90+rearAngle 270-rearAngle 270+frontAngle];
  %output = [90-45 90+32 270-24 270+89];
  %output = [90-(9+randi(71)) 90+(9+randi(71)) 270-(9+randi(71)) 270+(9+randi(71))];
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
    theta - phi(1) - pi/2;
    theta - phi(2) - pi/2;
    theta - phi(3) - pi/2;
    theta - phi(4) - pi/2;
  ];

  # Fwd/Inv kinematic model
  fkArr = [-sin(phi);cos(phi);ones(1,length(wheelAngleDeg{i}))];
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
  polar(maxRobotVelocity_angle+pi/2,maxRobotVelocity_magnitude,plotStyle{i});
  
  subplot(1,2,2);
  if(i == 1)
    hold off
  else
    hold on
  end
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


display('Min         Max         Mean       StdDev      CoV');
display(num2str(stats));
