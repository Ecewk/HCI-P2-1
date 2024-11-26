using UnityEngine;

public class parallaxScript : MonoBehaviour
{
    public Transform target;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        float speed = 0.5F;

        transform.RotateAround(target.position, transform.right, -Input.GetAxis("Mouse Y") * speed);
        transform.RotateAround(target.position, transform.up, -Input.GetAxis("Mouse X") * speed);
    }
}
