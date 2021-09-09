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
  [30 52];
]

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

# Convert wheel angles to radians
wheelAngleRad = cellfun(@(deg) deg2rad(deg),wheelAngleDeg,'un',0);

plotStyle = {'-r' '-g' '-b' '--r' '--g' '--b'};

# Robot-level Vectors
theta = deg2rad(linspace(0,360,sampleCount)); # robot heading
robotVelocity = [cos(theta);sin(theta);zeros(1,sampleCount)];

# Iterate over each wheel config
for i=1:length(wheelAngleDeg)
  phi = wheelAngleRad{i}; # load wheel config

  # Fwd/Inv kinematic model
  fkArr = [-sin(phi);cos(phi);ones(1,length(wheelAngleDeg{i}))];
  ikArr = pinv(fkArr);

  # Calculate individual wheel velocities based on robot velocity vector
  wheelVelocities = ikArr*robotVelocity;

  scaledwheelVelocities = wheelVelocities ./ max(abs(wheelVelocities),[],1);
  maxRobotVelocity = fkArr*scaledwheelVelocities;
  maxRobotVelocity_angle = atan2(maxRobotVelocity(2,:),maxRobotVelocity(1,:));
  maxRobotVelocity_magnitude = sqrt(maxRobotVelocity(1,:).^2+maxRobotVelocity(2,:).^2);

  stats = [
    stats;
    max(maxRobotVelocity_magnitude) mean(maxRobotVelocity_magnitude) std(maxRobotVelocity_magnitude)
  ];

  if(i == 1)
    hold off
  else
    hold on
  end
  # Plot with the Forward direction = 90deg
  polar(maxRobotVelocity_angle+pi/2,maxRobotVelocity_magnitude,plotStyle{i});

end

legend(legendLabel);


display('Max         Mean       StdDev');
display(num2str(stats));
