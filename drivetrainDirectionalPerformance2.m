clear
clc
close all

%% Notes
% 90deg on the plot is "forward"
% wheelConfig should be entered in degrees
%   Angles measured from the axis running left-to-right


%% User Configurable Parameters

wheelConfig = [ % Front/Rear Wheel Angles
  [45 45];
  [30 45];
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
wheelAngleDeg

# Convert wheel angles to radians
wheelAngleRad = cellfun(@(deg) deg2rad(deg),wheelAngleDeg,'un',0);

plotStyle = {'.r' '.g' '.b' '.r' '.g' '.b'};
plotTableLabels = {'Min','Max','Mean','StdDev','CoV','Side'};

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

  usefulWheelPower = [
    scaledWheelVelocities(1)*cos(psi(1,:));
    scaledWheelVelocities(2)*cos(psi(2,:));
    scaledWheelVelocities(3)*cos(psi(3,:));
    scaledWheelVelocities(4)*cos(psi(4,:));
  ];
  usefulWheelPower = abs(usefulWheelPower);

  scaledWheelVelocities = abs(scaledWheelVelocities);
  maxScaledwheelVelocity = max(scaledWheelVelocities);
  stdScaledwheelVelocity = std(scaledWheelVelocities);
  covScaledwheelVelocity = std(scaledWheelVelocities)/mean(scaledWheelVelocities);
  rangeScaledwheelVelocity = max(scaledWheelVelocities) - min(scaledWheelVelocities);
  [~, idx_side] = min(abs(maxRobotVelocity_angle - pi/2));
  maxRobotVelocity_magnitude_side = maxRobotVelocity_magnitude(idx_side);
  stats = [
    stats;
    min(maxRobotVelocity_magnitude) max(maxRobotVelocity_magnitude) mean(maxRobotVelocity_magnitude) std(maxRobotVelocity_magnitude) std(maxRobotVelocity_magnitude)/mean(maxRobotVelocity_magnitude) maxRobotVelocity_magnitude_side
  ];

  subplot(1,2,1);
  if(i == 1)
    hold off
  else
    hold on
  end
  # Plot with the Forward direction = 90deg
  polar(
    [maxRobotVelocity_angle+pi/2 maxRobotVelocity_angle+pi/2],
    [maxRobotVelocity_magnitude repmat(min(maxRobotVelocity_magnitude),1,sampleCount)],
    plotStyle{i}
  );

  subplot(1,2,2);
  axis off;
  if(i == 1)
    hold off
  else
    hold on
  end
  [r_stats, c_stats] = size(stats);
  for c = 1:c_stats
      text(0.2*c-0.4, 0.8, plotTableLabels{c}, "fontsize", 12);
      for r = 1:r_stats
          text(0.2*c-0.4, 0.8-r*0.05, num2str(stats(r,c)), "fontsize", 12);
      end
  end
  for i = 1:length(legendLabel)
    text(-0.4, 0.8-i*0.05, legendLabel{i}, "fontsize", 12);
  end

end

subplot(1,2,1);
legend(legendLabel);
set(findobj(gca, 'Type', 'Line'), 'MarkerSize', 3)

display('Min         Max         Mean       StdDev      CoV          Side');
display(num2str(stats));
