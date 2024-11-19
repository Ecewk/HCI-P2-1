using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BoidManager : MonoBehaviour
{
    const int threadGroupSize = 1024;

    public BoidSettings settings;
    public ComputeShader compute;
    Boid[] boids;

    void Start()
    {
        boids = FindObjectsOfType<Boid>();
        foreach (Boid b in boids)
        {
            b.Initialize(b.settings);
        }
    }

    void Update()
    {
        if (boids != null && boids.Length > 0)
        {
            // Group boids by their groupID
            var groupedBoids = GroupBoidsByGroupID();

            foreach (var group in groupedBoids)
            {
                var groupBoids = group.Value; // Boids in the same group
                int numBoids = groupBoids.Count;

                var boidData = new BoidData[numBoids];
                for (int i = 0; i < numBoids; i++)
                {
                    boidData[i].position = groupBoids[i].position;
                    boidData[i].direction = groupBoids[i].forward;
                }

                var boidBuffer = new ComputeBuffer(numBoids, BoidData.Size);
                boidBuffer.SetData(boidData);

                compute.SetBuffer(0, "boids", boidBuffer);
                compute.SetInt("numBoids", numBoids);
                compute.SetFloat("viewRadius", settings.perceptionRadius);
                compute.SetFloat("avoidRadius", settings.avoidanceRadius);

                int threadGroups = Mathf.CeilToInt(numBoids / (float)threadGroupSize);
                compute.Dispatch(0, threadGroups, 1, 1);

                boidBuffer.GetData(boidData);

                for (int i = 0; i < numBoids; i++)
                {
                    groupBoids[i].avgFlockHeading = boidData[i].flockHeading;
                    groupBoids[i].centreOfFlockmates = boidData[i].flockCentre;
                    groupBoids[i].avgAvoidanceHeading = boidData[i].avoidanceHeading;
                    groupBoids[i].numPerceivedFlockmates = boidData[i].numFlockmates;

                    UpdateBoidBehavior(groupBoids[i]);
                }

                boidBuffer.Release();
            }
        }
    }

    void UpdateBoidBehavior(Boid boid)
    {
        // Afraid Behavior: Avoid objects in the "afraidOfMask" layer
        Vector3 avoidForce = boid.GetAvoidanceForce(boid.settings.boundsRadius * 10, boid.settings.afraidAvoidDistance, boid.settings.afraidOfMask);
        if (avoidForce != boid.forward)
        {
            boid.UpdateBoidWithForce(avoidForce, boid.settings.afraidAvoidWeight);
            return; // Exit early to prioritize avoidance
        }

        // Likes Behavior: Move towards objects in the "likes" layer
        Vector3 followForce = boid.GetAvoidanceForce(boid.settings.boundsRadius, boid.settings.likesDistance, boid.settings.likes);
        if (followForce != boid.forward)
        {
            boid.UpdateBoidWithForce(followForce, boid.settings.likesWeight);
            return; // Exit early to prioritize following
        }

        // Normal Behavior: Alignment, cohesion, separation, and collision avoidance
        boid.UpdateBoid();
    }

    private Dictionary<string, List<Boid>> GroupBoidsByGroupID()
    {
        var groupedBoids = new Dictionary<string, List<Boid>>();

        foreach (Boid boid in boids)
        {
            if (!groupedBoids.ContainsKey(boid.groupID))
            {
                groupedBoids[boid.groupID] = new List<Boid>();
            }
            groupedBoids[boid.groupID].Add(boid);
        }

        return groupedBoids;
    }

    public struct BoidData
    {
        public Vector3 position;
        public Vector3 direction;

        public Vector3 flockHeading;
        public Vector3 flockCentre;
        public Vector3 avoidanceHeading;
        public int numFlockmates;

        public static int Size
        {
            get
            {
                return sizeof(float) * 3 * 5 + sizeof(int);
            }
        }
    }
}
