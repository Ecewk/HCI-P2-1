using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class keys : MonoBehaviour
{
    public float speed = 10.0f;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        float translationX = Input.GetAxis("Horizontal") * speed * Time.deltaTime;
        float translationZ = Input.GetAxis("Vertical") * speed * Time.deltaTime;
        float translationY = 0;

        if (Input.GetKey(KeyCode.Space))
        {
            translationY = speed * Time.deltaTime;
        }
        else if (Input.GetKey(KeyCode.LeftShift))
        {
            translationY = -speed * Time.deltaTime;
        }

        transform.Translate(translationX, translationY, translationZ);
    }
}