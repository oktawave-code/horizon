import { Schema, Mixed } from 'mongoose';

export const GraphSchema = new Schema({
    clientId: { type: String, index: true },
    name: String,
    graph: Mixed
  }, {
    timestamps: true
  });

// Ensure virtual fields are serialised.
GraphSchema.set('toJSON', {
  virtuals: true,
  transform: function(doc, ret, options) {
    // remove the _id of every document before returning the result
    ret.id = ret._id;
    delete ret._id;
  }
});