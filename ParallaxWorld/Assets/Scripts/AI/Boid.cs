using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Boid : MonoBehaviour
{
    public BoidSettings settings;
    public string groupID; // Unique identifier for boid groups (e.g., prefab name)

    // State
    [HideInInspector]
    public Vector3 position;
    [HideInInspector]
    public Vector3 forward;
    Vector3 velocity;

    // To update:
    Vector3 acceleration;
    [HideInInspector]
    public Vector3 avgFlockHeading;
    [HideInInspector]
    public Vector3 avgAvoidanceHeading;
    [HideInInspector]
    public Vector3 centreOfFlockmates;
    [HideInInspector]
    public int numPerceivedFlockmates;

    // Cached
    Material material;
    Transform cachedTransform;

    void Awake()
    {
        material = transform.GetComponentInChildren<MeshRenderer>()?.material;
        cachedTransform = transform;
    }

    public void Initialize(BoidSettings settings)
    {
        this.settings = settings;

        position = cachedTransform.position;
        forward = cachedTransform.forward;

        float startSpeed = (settings.minSpeed + settings.maxSpeed) / 2;
        velocity = transform.forward * startSpeed;
    }

    public void SetColour(Color col)
    {
        if (material != null)
        {
            material.color = col;
        }
    }

    public void UpdateBoid()
    {
        if (settings == null)
        {
            Debug.LogError("Boid settings are not initialized.");
            return;
        }

        Vector3 acceleration = Vector3.zero;

        // Alignment, Cohesion, and Separation
        if (numPerceivedFlockmates > 0)
        {
            centreOfFlockmates /= numPerceivedFlockmates;
            Vector3 offsetToFlockmatesCentre = (centreOfFlockmates - position);

            var alignmentForce = SteerTowards(avgFlockHeading) * settings.alignWeight;
            var cohesionForce = SteerTowards(offsetToFlockmatesCentre) * settings.cohesionWeight;
            var separationForce = SteerTowards(avgAvoidanceHeading) * settings.seperateWeight;

            acceleration += alignmentForce;
            acceleration += cohesionForce;
            acceleration += separationForce;
        }

        // Collision Avoidance
        if (IsHeadingForCollision())
        {
            Vector3 collisionAvoidDir = ObstacleRays();
            Vector3 collisionAvoidForce = SteerTowards(collisionAvoidDir) * settings.avoidCollisionWeight;
            acceleration += collisionAvoidForce;
        }

        UpdateVelocity(acceleration);
    }

    public void UpdateBoidWithForce(Vector3 force, float weight)
    {
        Vector3 weightedForce = force.normalized * weight;
        UpdateVelocity(weightedForce);
    }

    void UpdateVelocity(Vector3 additionalAcceleration)
    {
        velocity += additionalAcceleration * Time.deltaTime;
        float speed = velocity.magnitude;
        Vector3 dir = velocity / speed;
        speed = Mathf.Clamp(speed, settings.minSpeed, settings.maxSpeed);
        velocity = dir * speed;

        cachedTransform.position += velocity * Time.deltaTime;
        cachedTransform.forward = dir;
        position = cachedTransform.position;
        forward = dir;
    }

    bool IsHeadingForCollision()
    {
        RaycastHit hit;
        return Physics.SphereCast(position, settings.boundsRadius, forward, out hit, settings.collisionAvoidDst, settings.obstacleMask);
    }

    public Vector3 ObstacleRays()
    {
        return GetAvoidanceForce(settings.boundsRadius, settings.collisionAvoidDst, settings.obstacleMask);
    }

    public Vector3 GetAvoidanceForce(float boundsRadius, float avoidanceDistance, LayerMask mask)
    {
        Vector3[] rayDirections = BoidHelper.directions;

        foreach (Vector3 dir in rayDirections)
        {
            Vector3 worldDir = cachedTransform.TransformDirection(dir);
            Ray ray = new Ray(position, worldDir);
            if (!Physics.SphereCast(ray, boundsRadius, avoidanceDistance, mask))
            {
                return worldDir; // return the direction we can move safely
            }
        }

        return forward; // default to moving forward if no avoidance is needed
    }

    Vector3 SteerTowards(Vector3 vector)
    {
        Vector3 v = vector.normalized * settings.maxSpeed - velocity;
        return Vector3.ClampMagnitude(v, settings.maxSteerForce);
    }
}
